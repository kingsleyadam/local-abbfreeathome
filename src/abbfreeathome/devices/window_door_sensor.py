"""Free@Home WindowDoorSensor Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class WindowDoorSensor(Base):
    """Free@Home WindowDoorSensor Class."""

    _state = None

    def __init__(
        self,
        device_id: str,
        device_name: str,
        channel_id: str,
        channel_name: str,
        inputs: dict[str, dict[str, Any]],
        outputs: dict[str, dict[str, Any]],
        parameters: dict[str, dict[str, Any]],
        api: FreeAtHomeApi,
        floor_name: str | None = None,
        room_name: str | None = None,
    ) -> None:
        """Initialize the Free@Home SwitchSensor class."""
        super().__init__(
            device_id,
            device_name,
            channel_id,
            channel_name,
            inputs,
            outputs,
            parameters,
            api,
            floor_name,
            room_name,
        )

        # Set the initial state of the switch based on output
        self._refresh_state_from_outputs()

    @property
    def state(self) -> bool | None:
        """Get the sensor state."""
        return self._state

    async def refresh_state(self):
        """Refresh the state of the device from the api."""
        _state_refresh_pairings = [
            Pairing.AL_WINDOW_DOOR,
        ]

        for _pairing in _state_refresh_pairings:
            _sensor_output_id, _sensor_output_value = self.get_output_by_pairing(
                pairing=_pairing
            )

            _datapoint = (
                await self._api.get_datapoint(
                    device_id=self.device_id,
                    channel_id=self.channel_id,
                    datapoint=_sensor_output_id,
                )
            )[0]

            self._refresh_state_from_output(
                output={
                    "pairingID": _pairing.value,
                    "value": _datapoint,
                }
            )

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_WINDOW_DOOR.value:
            self._state = output.get("value") == "1"
            return True
        return False
