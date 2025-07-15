"""Free@Home MovementDetectorSensor Class."""

from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


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
        device: "Device",
        channel_id: str,
        channel_name: str,
        inputs: dict[str, dict[str, Any]],
        outputs: dict[str, dict[str, Any]],
        parameters: dict[str, dict[str, Any]],
        floor_name: str | None = None,
        room_name: str | None = None,
    ) -> None:
        """Initialize the Free@Home MovementDetector class."""
        self._state: bool | None = None
        self._brightness: float | None = None

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
        """Get the movement state."""
        return self._state

    @property
    def brightness(self) -> float | None:
        """Get the brightness level of the sensor."""
        return self._brightness

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if datapoint.get("pairingID") == Pairing.AL_TIMED_MOVEMENT.value:
            self._state = datapoint.get("value") == "1"
            return "state"
        if datapoint.get("pairingID") == Pairing.AL_BRIGHTNESS_LEVEL.value:
            self._brightness = float(datapoint.get("value"))
            return "brightness"
        return None
