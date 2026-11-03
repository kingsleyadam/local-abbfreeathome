"""Free@Home virtual DimActuator channel."""

import enum
import logging
from typing import TYPE_CHECKING, Any

from ...bin.pairing import Pairing
from .virtual_switch_actuator import VirtualSwitchActuator

if TYPE_CHECKING:
    from ...device import Device

_LOGGER = logging.getLogger(__name__)


class VirtualDimmingRequestState(enum.Enum):
    """
    Relative dimming requests received by a virtual dimmer.

    Requests are 4-bit relative dimming commands: bit 3 is the direction
    (1 = up) and bits 0-2 the step size, where 0 means stop. Physical sensors
    send 9/1 for a long press and 8/0 on release; the free@home app sends 15/7
    for its +/- buttons, each followed by 0.
    """

    unknown = None
    longpress_up = "longpress_up"
    longpress_up_release = "longpress_up_release"
    longpress_down = "longpress_down"
    longpress_down_release = "longpress_down_release"
    step_up = "step_up"
    step_down = "step_down"
    stop = "stop"


_RELATIVE_DIMMING_REQUESTS = {
    ("longpress", True): VirtualDimmingRequestState.longpress_up,
    ("longpress", False): VirtualDimmingRequestState.longpress_down,
    ("release", True): VirtualDimmingRequestState.longpress_up_release,
    ("release", False): VirtualDimmingRequestState.longpress_down_release,
    ("step", True): VirtualDimmingRequestState.step_up,
    ("step", False): VirtualDimmingRequestState.step_down,
}


class VirtualDimmingActuator(VirtualSwitchActuator):
    """Receive dimming requests and publish virtual actuator feedback."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_ON_OFF,
        Pairing.AL_INFO_ACTUAL_DIMMING_VALUE,
    ]

    _input_refresh_pairings: list[Pairing] = [
        Pairing.AL_SWITCH_ON_OFF,
        Pairing.AL_RELATIVE_SET_VALUE_CONTROL,
        Pairing.AL_ABSOLUTE_SET_VALUE_CONTROL,
    ]
    _callback_attributes: list[str] = [
        "state",
        "brightness",
        "requested_state",
        "requested_dimming_state",
        "requested_brightness",
    ]

    def __init__(
        self,
        device: "Device",
        channel_id: str,
        channel_name: str,
        inputs: dict[str, dict[str, Any]],
        outputs: dict[str, dict[str, Any]],
        parameters: dict[str, dict[str, Any]],
        floor_name: str | None = None,
        room_name: str | None = None,
    ) -> None:
        """Initialize the virtual dimmer and its requested states."""
        self._brightness: int | None = None
        self._requested_dimming_state = VirtualDimmingRequestState.unknown
        self._requested_brightness: float | None = None
        super().__init__(
            device,
            channel_id,
            channel_name,
            inputs,
            outputs,
            parameters,
            floor_name,
            room_name,
        )
        # The inherited update handler also accepts updates without subscribers.
        for attribute in self._callback_attributes:
            self._callbacks[attribute] = set()

    @property
    def brightness(self) -> int | None:
        """Return reported brightness, independently of requested brightness."""
        return self._brightness

    async def set_brightness(self, value: int):
        """Publish brightness feedback, clamping integer percentages to 1-100."""
        if isinstance(value, bool) or not isinstance(value, int):
            message = "Brightness must be an integer percentage"
            raise TypeError(message)
        value = min(100, max(1, value))
        await self._set_brightness_datapoint(str(value))
        self._brightness = value

    async def _set_brightness_datapoint(self, value: str):
        """Publish brightness to the virtual output, not the request input."""
        output_id, _ = self.get_output_by_pairing(Pairing.AL_INFO_ACTUAL_DIMMING_VALUE)
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=output_id,
            value=value,
        )

    @property
    def requested_dimming_state(self) -> str:
        """
        Return the VirtualDimmingRequestState name, not an absolute brightness.

        9/1 mean longpress_up/longpress_down and 8/0 their releases, as sent by
        a physical DimmingSensor. Other steps (10-15/2-7, such as the app's
        +/- buttons) mean step_up/step_down, and a following 8/0 means stop.
        Unrecognized commands are exposed as unknown.
        """
        return self._requested_dimming_state.name

    @property
    def requested_brightness(self) -> float | None:
        """Return the last valid requested percentage, not actual brightness."""
        return self._requested_brightness

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> list[str]:
        """Decode reported brightness and requests independently."""
        pairing = datapoint.get("pairingID")
        if pairing in (
            Pairing.AL_ABSOLUTE_SET_VALUE_CONTROL.value,
            Pairing.AL_INFO_ACTUAL_DIMMING_VALUE.value,
        ):
            feedback = pairing == Pairing.AL_INFO_ACTUAL_DIMMING_VALUE.value
            label = "brightness feedback" if feedback else "requested brightness"
            value = datapoint.get("value")
            if value is None or value == "":
                _LOGGER.debug("No %s for %s", label, self.channel_name)
                return []
            try:
                brightness = float(value)
            except (TypeError, ValueError, OverflowError):
                _LOGGER.warning("Invalid %s %r for %s", label, value, self.channel_name)
                return []
            if isinstance(value, bool) or not 0 <= brightness <= 100:
                _LOGGER.warning(
                    "%s %r outside 0-100 percent for %s",
                    label,
                    value,
                    self.channel_name,
                )
                return []
            if feedback:
                self._brightness = int(brightness)
            else:
                self._requested_brightness = brightness
            return ["brightness" if feedback else "requested_brightness"]
        if datapoint.get("pairingID") == Pairing.AL_RELATIVE_SET_VALUE_CONTROL.value:
            self._requested_dimming_state = self._decode_relative_dimming(
                datapoint.get("value")
            )
            return ["requested_dimming_state"]
        return super()._refresh_state_from_datapoint(datapoint)

    def _decode_relative_dimming(self, value: Any) -> VirtualDimmingRequestState:
        """Decode a 4-bit relative dimming command, see VirtualDimmingRequestState."""
        if value is None or value == "":
            _LOGGER.debug("No requested dimming state for %s", self.channel_name)
            return VirtualDimmingRequestState.unknown
        if not isinstance(value, str) or not value.isdecimal() or int(value) > 15:
            _LOGGER.warning(
                "Invalid requested dimming state %r for %s", value, self.channel_name
            )
            return VirtualDimmingRequestState.unknown
        command = int(value)
        up = bool(command & 0b1000)
        step = command & 0b0111
        if step == 0:
            # A stop after a step (or a repeated stop) ends the step, not a press.
            if self._requested_dimming_state in (
                VirtualDimmingRequestState.step_up,
                VirtualDimmingRequestState.step_down,
                VirtualDimmingRequestState.stop,
            ):
                return VirtualDimmingRequestState.stop
            kind = "release"
        elif step == 1:
            kind = "longpress"
        else:
            kind = "step"
        return _RELATIVE_DIMMING_REQUESTS[kind, up]
