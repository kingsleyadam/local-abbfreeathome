"""Free@Home CarbonMonoxideSensor Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class CarbonMonoxideSensor(Base):
    """Free@Home CarbonMonoxideSensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_CO_ALARM_ACTIVE,
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
    ) -> None:
        """Initialize the Free@Home CarbonMonoxideSensor class."""
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
        """Get the device state."""
        return self._state

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if datapoint.get("pairingID") == Pairing.AL_CO_ALARM_ACTIVE.value:
            self._state = datapoint.get("value") == "1"
            return "state"
        return None
