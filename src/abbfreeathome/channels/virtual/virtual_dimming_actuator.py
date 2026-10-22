"""Free@Home virtual DimActuator channel."""

from typing import TYPE_CHECKING, Any

from ...bin.pairing import Pairing
from ..switch_sensor import DimmingSensorState
from .virtual_switch_actuator import VirtualSwitchActuator

if TYPE_CHECKING:
    from ...device import Device


class VirtualDimmingActuator(VirtualSwitchActuator):
    """Receive switching and relative dimming requests from linked sensors."""

    _input_refresh_pairings: list[Pairing] = [
        Pairing.AL_SWITCH_ON_OFF,
        Pairing.AL_RELATIVE_SET_VALUE_CONTROL,
    ]
    _callback_attributes: list[str] = [
        "state",
        "requested_state",
        "requested_dimming_state",
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
        self._requested_dimming_state = DimmingSensorState.unknown
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
    def requested_dimming_state(self) -> str:
        """
        Return the DimmingSensorState name, not an absolute brightness.

        Values 9/8 mean longpress_up/longpress_up_release; 1/0 mean
        longpress_down/longpress_down_release, as on a physical DimmingSensor.
        Unrecognized commands are exposed as unknown.
        """
        return self._requested_dimming_state.name

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str | None:
        """Decode relative requests using the physical sensor's command enum."""
        if datapoint.get("pairingID") == Pairing.AL_RELATIVE_SET_VALUE_CONTROL.value:
            try:
                self._requested_dimming_state = DimmingSensorState(
                    datapoint.get("value")
                )
            except ValueError:
                self._requested_dimming_state = DimmingSensorState.unknown
            return "requested_dimming_state"
        return super()._refresh_state_from_datapoint(datapoint)

    def _refresh_state_from_datapoints(self):
        """Initialize feedback and requests from the configuration snapshot."""
        super()._refresh_state_from_datapoints()
        for datapoint in self._inputs.values():
            if datapoint.get("pairingID") in [
                pairing.value for pairing in self._input_refresh_pairings
            ]:
                self._refresh_state_from_datapoint(datapoint)

    async def refresh_state(self):
        """Refresh feedback and available request inputs from the API."""
        await super().refresh_state()
        for datapoint_id, datapoint in self._inputs.items():
            if datapoint.get("pairingID") in [
                pairing.value for pairing in self._input_refresh_pairings
            ]:
                value = (
                    await self.device.api.get_datapoint(
                        device_serial=self.device_serial,
                        channel_id=self.channel_id,
                        datapoint=datapoint_id,
                    )
                )[0]
                datapoint["value"] = value
                self._refresh_state_from_datapoint(datapoint)
