"""Free@Home HeatingActuator Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class HeatingActuator(Base):
    """Free@Home HeatingActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_VALUE_HEATING,
    ]
    _callback_attributes: list[str] = [
        "position",
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
    ) -> None:
        """Initialize the Free@Home HeatingActuator class."""
        self._position: int | None = None

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
    def position(self) -> int | None:
        """Get the position of the actuator."""
        return self._position

    async def set_position(self, value: int):
        """
        Set the position of the valve.

        The position has to be between 0 and 100
        Fully closed = 0
        Fully open = 100
        """
        value = max(0, value)
        value = min(value, 100)

        await self._set_position_datapoint(str(value))
        self._position = value

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if datapoint.get("pairingID") == Pairing.AL_INFO_VALUE_HEATING.value:
            self._position = int(float(datapoint.get("value")))
            return "position"
        return None

    async def _set_position_datapoint(self, value: str):
        """Set the position datapoint on the api."""
        _position_input_id, _position_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_ACTUATING_VALUE_HEATING
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_position_input_id,
            value=value,
        )
