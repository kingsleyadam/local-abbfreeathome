"""Free@Home MovementDetectorSensor Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class MovementDetector(Base):
    """Free@Home MovementDetector Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_BRIGHTNESS_LEVEL,
        Pairing.AL_TIMED_MOVEMENT,
    ]
    _callback_attributes: list[str] = [
        "state",
        "brightness",
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
        """Initialize the Free@Home MovementDetector class."""
        self._state: bool | None = None
        self._brightness: float | None = None

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
        """Get the movement state."""
        return self._state

    @property
    def brightness(self) -> float | None:
        """Get the brightness level of the sensor."""
        return self._brightness

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if datapoint.get("pairingID") == Pairing.AL_TIMED_MOVEMENT.value:
            self._state = datapoint.get("value") == "1"
            return "state"
        if datapoint.get("pairingID") == Pairing.AL_BRIGHTNESS_LEVEL.value:
            self._brightness = float(datapoint.get("value"))
            return "brightness"
        return None
