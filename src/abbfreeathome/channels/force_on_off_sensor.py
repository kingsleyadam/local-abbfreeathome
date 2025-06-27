"""Free@Home ForceOnOffSensor Class."""

import enum
from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class ForceOnOffSensorState(enum.Enum):
    """An Enum class for the force on off sensor states."""

    unknown = None
    off = "0"
    on = "1"


class ForceOnOffSensor(Base):
    """Free@Home ForceOnOffSensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_FORCED,
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
        """Initialize the Free@Home ForceOnOffSensor class."""
        self._state: ForceOnOffSensorState = ForceOnOffSensorState.unknown

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
        """Get the forceOnOff state."""
        return self._state.name

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if datapoint.get("pairingID") == Pairing.AL_FORCED.value:
            """
            Forces value dependent high priority on or off state

            If the rocker is configured as 'force on':
            3 means on
            1 means off
            If the rocker is configured as 'force off':
            2 means on
            0 means off
            """
            if datapoint.get("value") in ("2", "3"):
                self._state = ForceOnOffSensorState.on
            elif datapoint.get("value") in ("0", "1"):
                self._state = ForceOnOffSensorState.off
            else:
                self._state = ForceOnOffSensorState.unknown
            return "state"
        return None
