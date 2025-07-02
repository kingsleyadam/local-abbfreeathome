"""Free@Home WindowDoorSensor Class."""

import enum
from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class WindowDoorSensorPosition(enum.Enum):
    """
    An Enum class for window/door sensor possible positions.

    Home Assistant requires the name to be all lowercase.
    """

    unknown = None
    closed = "0"
    tilted = "33"
    open = "100"


class WindowDoorSensor(Base):
    """Free@Home WindowDoorSensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_WINDOW_DOOR,
    ]
    _callback_attributes: list[str] = [
        "state",
        "position",
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
        """Initialize the Free@Home WindowDoorSensor class."""
        self._state: bool | None = None
        self._position: WindowDoorSensorPosition = WindowDoorSensorPosition.unknown

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
        """Get the sensor state."""
        return self._state

    @property
    def position(self) -> str | None:
        """Get the sensor position."""
        return self._position.name

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if datapoint.get("pairingID") == Pairing.AL_WINDOW_DOOR.value:
            self._state = datapoint.get("value") == "1"
            return "state"
        if datapoint.get("pairingID") == Pairing.AL_WINDOW_DOOR_POSITION.value:
            try:
                self._position = WindowDoorSensorPosition(datapoint.get("value"))
            except ValueError:
                self._position = WindowDoorSensorPosition.unknown
            return "position"
        return None
