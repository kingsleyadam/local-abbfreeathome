"""Free@Home BlindSensor Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class BlindSensor(Base):
    """Free@Home BlindSensor Class."""

    _state_refresh_output_pairings: list[Pairing] = [
        Pairing.AL_MOVE_UP_DOWN,
        Pairing.AL_STOP_STEP_UP_DOWN,
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
        """Initialize the Free@Home BlindSensor class."""
        self._state: bool | None = None
        self._longpress: bool | None = None

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

    @property
    def longpress(self) -> bool | None:
        """Get the info, if the rocker was long pressed."""
        return self._longpress

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_STOP_STEP_UP_DOWN.value:
            """
            0 means up was pressed
            1 means down was pressed
            """
            self._state = output.get("value") == "1"
            return True
        if output.get("pairingID") == Pairing.AL_MOVE_UP_DOWN.value:
            """
            0 means up was long pressed
            1 means down was long pressed
            """
            self._longpress = output.get("value") == "1"
            return True
        return False
