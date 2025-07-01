"""Free@Home BlindSensor Class."""

import enum
from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class BlindSensorState(enum.Enum):
    """An Enum class for the blind sensor state."""

    unknown = None
    step_up = "0"
    step_down = "1"
    move_up = "2"
    move_down = "3"


class BlindSensor(Base):
    """Free@Home BlindSensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_MOVE_UP_DOWN,
        Pairing.AL_STOP_STEP_UP_DOWN,
    ]
    _callback_attributes: list[str] = [
        "state",
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
        """Initialize the Free@Home BlindSensor class."""
        self._state: BlindSensorState = BlindSensorState.unknown
        self._step_state: BlindSensorState = BlindSensorState.unknown
        self._move_state: BlindSensorState = BlindSensorState.unknown

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
    def state(self) -> str:
        """Get the sensor state."""
        return self._state.name

    @property
    def step_state(self) -> str:
        """Get the step state property."""
        return self._step_state.name

    @property
    def move_state(self) -> str:
        """Get the move state property."""
        return self._move_state.name

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if datapoint.get("pairingID") == Pairing.AL_STOP_STEP_UP_DOWN.value:
            """
            Stops the sunblind and to step it up/down

            0 means up was pressed
            1 means down was pressed
            """
            if datapoint.get("value") == "0":
                self._step_state = BlindSensorState.step_up
            elif datapoint.get("value") == "1":
                self._step_state = BlindSensorState.step_down
            else:
                self._step_state = BlindSensorState.unknown

            self._state = self._step_state
            return "state"

        if datapoint.get("pairingID") == Pairing.AL_MOVE_UP_DOWN.value:
            """
            Moves sunblind up (0) and down (1)

            0 means up was pressed
            1 means down was pressed
            """
            if datapoint.get("value") == "0":
                self._move_state = BlindSensorState.move_up
            elif datapoint.get("value") == "1":
                self._move_state = BlindSensorState.move_down
            else:
                self._move_state = BlindSensorState.unknown

            self._state = self._move_state
            return "state"
        return None
