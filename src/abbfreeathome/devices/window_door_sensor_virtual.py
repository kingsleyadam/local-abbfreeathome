"""Free@Home WindowDoorSensorVirtual Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class WindowDoorSensorVirtual(Base):
    """Free@Home WindowDoorSensorVirtual Class."""

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
        """Initialize the Free@Home WindowDoorSensorVirtual class."""
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

    async def open(self):
        """Open the sensor."""
        await self._set_switching_datapoint("1")
        self._state = True

    async def close(self):
        """Close the sensor."""
        await self._set_switching_datapoint("0")
        self._state = False

    async def _set_switching_datapoint(self, value: str):
        """Set the sensor datapoint on the api."""
        _output_id, _output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_WINDOW_DOOR
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_output_id,
            value=value,
        )
