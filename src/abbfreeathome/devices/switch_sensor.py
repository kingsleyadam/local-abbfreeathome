"""Free@Home SwitchSensor Class."""

import enum
from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class SwitchSensorState(enum.Enum):
    """An Enum class for the switch sensor states."""

    unknown = None
    off = "0"
    on = "1"


class DimmingSensorState(enum.Enum):
    """An Enum class for the dimming sensor states."""

    unknown = None
    longpress_up = "9"
    longpress_up_release = "8"
    longpress_down = "1"
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
        self._state: SwitchSensorState | DimmingSensorState = SwitchSensorState.unknown
        self._switch_sensor_state: SwitchSensorState = SwitchSensorState.unknown
        self._dimming_sensor_state: DimmingSensorState = DimmingSensorState.unknown

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
    def state(self) -> str:
        """Get the state."""
        return self._state.name

    @property
    def switching_state(self) -> str:
        """Get the switch state."""
        return self._switch_sensor_state.name

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_SWITCH_ON_OFF.value:
            try:
                self._switch_sensor_state = SwitchSensorState(output.get("value"))
            except ValueError:
                self._switch_sensor_state = SwitchSensorState.unknown

            self._state = self._switch_sensor_state
            return True
        return False


class DimmingSensor(SwitchSensor):
    """Free@Home DimmingSensor Class."""

    @property
    def dimming_state(self) -> str:
        """Get the dimming state."""
        return self._dimming_sensor_state.name

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if super()._refresh_state_from_output(output):
            return True

        if output.get("pairingID") == Pairing.AL_RELATIVE_SET_VALUE_CONTROL.value:
            try:
                self._dimming_sensor_state = DimmingSensorState(output.get("value"))
            except ValueError:
                self._dimming_sensor_state = DimmingSensorState.unknown

            self._state = self._dimming_sensor_state
            return True
        return False
