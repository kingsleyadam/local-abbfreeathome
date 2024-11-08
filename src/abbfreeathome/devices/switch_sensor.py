"""Free@Home SwitchSensor Class."""

import enum
from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class DimmingSensorLongpressState(enum.Enum):
    """An Enum class for the longpress states."""

    unknown = None
    longpress_up_press = "9"
    longpress_up_release = "8"
    longpress_down_press = "1"
    longpress_down_release = "0"


class SwitchSensor(Base):
    """Free@Home SwitchSensor Class."""

    _state_refresh_output_pairings: list[Pairing] = [
        Pairing.AL_RELATIVE_SET_VALUE_CONTROL,
        Pairing.AL_SWITCH_ON_OFF,
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
        """Initialize the Free@Home SwitchSensor class."""
        self._state: bool | None = None
        self._longpress: DimmingSensorLongpressState = (
            DimmingSensorLongpressState.unknown
        )

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
        """Get the switch state."""
        return self._state

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_SWITCH_ON_OFF.value:
            self._state = output.get("value") == "1"
            return True
        if output.get("pairingID") == Pairing.AL_RELATIVE_SET_VALUE_CONTROL.value:
            try:
                self._longpress = DimmingSensorLongpressState(output.get("value"))
            except ValueError:
                self._longpress = DimmingSensorLongpressState.unknown
            return True
        return False


class DimmingSensor(SwitchSensor):
    """Free@Home DimmingSensor Class."""

    @property
    def longpress(self) -> str | None:
        """Get the longpress value."""
        return self._longpress.name
