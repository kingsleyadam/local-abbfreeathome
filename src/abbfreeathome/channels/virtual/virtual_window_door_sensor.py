"""Free@Home Virtual WindowDoorSensor Class."""

from typing import Any

from ...api import FreeAtHomeApi
from ...bin.pairing import Pairing
from ..base import Base


class VirtualWindowDoorSensor(Base):
    """Free@Home Virtual WindowDoorSensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_WINDOW_DOOR,
    ]
    _callback_attributes: list[str] = [
        "state",
    ]

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
    ):
        """Initialize the Free@Home Virtual WindowDoorSensor class."""
        self._state: bool | None = None

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

    @property
    def state(self) -> bool | None:
        """Get the sensor state."""
        return self._state

    async def turn_on(self):
        """Turn on the sensor."""
        await self._set_switching_datapoint("1")
        self._state = True

    async def turn_off(self):
        """Turn off the sensor."""
        await self._set_switching_datapoint("0")
        self._state = False

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if datapoint.get("pairingID") == Pairing.AL_WINDOW_DOOR.value:
            self._state = datapoint.get("value") == "1"
            return "state"

        return None

    async def _set_switching_datapoint(self, value: str):
        """Set the sensor datapoint on the api."""
        _sensor_output_id, _sensor_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_WINDOW_DOOR
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_sensor_output_id,
            value=value,
        )
