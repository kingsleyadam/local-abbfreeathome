"""Free@Home Virtual SwitchActuator class."""

# import enum
import logging
from typing import TYPE_CHECKING, Any

from ...bin.pairing import Pairing
from ..base import Base

if TYPE_CHECKING:
    from ...device import Device

_LOGGER = logging.getLogger(__name__)


class VirtualSwitchActuator(Base):
    """Free@Home Virtual SwitchActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_ON_OFF,
    ]

    _input_refresh_pairings: list[Pairing] = [
        Pairing.AL_SWITCH_ON_OFF,
    ]
    _callback_attributes: list[str] = [
        "state",
        "requested_state",
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
        """Initialize the Free@Home Virtual SwitchActuator class."""
        self._state: bool | None = None
        self._requested_state: bool | None = None

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

    @property
    def state(self) -> bool | None:
        """Get the state of the switch."""
        return self._state

    @property
    def requested_state(self) -> bool | None:
        """Get the requested state of the switch."""
        return self._requested_state

    async def turn_on(self):
        """Turn on the switch."""
        await self._set_switching_datapoint("1")
        self._state = True

    async def turn_off(self):
        """Turn off the switch."""
        await self._set_switching_datapoint("0")
        self._state = False

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> list[str]:
        """
        Refresh the state of the channel from a given output.

        Return the names of the attributes refreshed by this datapoint.
        """
        if datapoint.get("pairingID") == Pairing.AL_SWITCH_ON_OFF.value:
            self._requested_state = datapoint.get("value") == "1"
            return ["requested_state"]
        if datapoint.get("pairingID") == Pairing.AL_INFO_ON_OFF.value:
            self._state = datapoint.get("value") == "1"
            return ["state"]
        return []

    async def _set_switching_datapoint(self, value: str):
        """Set the switching datapoint on the api."""
        _switch_output_id, _switch_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_INFO_ON_OFF
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_switch_output_id,
            value=value,
        )

    def update_channel(
        self, datapoint_key: str, datapoint_value: str, is_priming: bool = False
    ):
        """Update the device state."""
        _LOGGER.info(
            "%s received updated data: %s: %s",
            self.channel_name,
            datapoint_key,
            datapoint_value,
        )
        _callback_attributes: list[str] = []
        _changed = True
        _io_key = datapoint_key.rsplit("/", maxsplit=1)[-1]

        if _io_key in self._outputs:
            _changed = self._outputs[_io_key].get("value") != datapoint_value
            self._outputs[_io_key]["value"] = datapoint_value
            _callback_attributes = self._refresh_state_from_datapoint(
                datapoint=self._outputs[_io_key]
            )

        if _io_key in self._inputs:
            _changed = self._inputs[_io_key].get("value") != datapoint_value
            self._inputs[_io_key]["value"] = datapoint_value
            _callback_attributes = self._refresh_state_from_datapoint(
                datapoint=self._inputs[_io_key]
            )

        if is_priming and not _changed:
            return

        self._notify_callbacks(_callback_attributes)

    def update_scene(
        self, datapoint_key: str, datapoint_value: str, is_priming: bool = False
    ):
        """Update scene output state and notify subscribers of its switch request."""
        self.update_channel(datapoint_key, datapoint_value, is_priming=is_priming)

        _io_key = datapoint_key.rsplit("/", maxsplit=1)[-1]
        _output = self._outputs.get(_io_key, {})
        if _output.get("pairingID") != Pairing.AL_INFO_ON_OFF.value:
            return

        # A triggered scene is a command, even if its value is unchanged or the
        # websocket is priming. Ordinary output feedback must not emit requests.
        self._requested_state = datapoint_value == "1"
        for callback in self._callbacks.get("requested_state", ()):
            callback()
