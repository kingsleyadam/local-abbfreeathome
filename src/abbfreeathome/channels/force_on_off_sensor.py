"""Free@Home ForceOnOffSensor Class."""

import enum
from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


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
        device: "Device",
        channel_id: str,
        channel_name: str,
        inputs: dict[str, dict[str, Any]],
        outputs: dict[str, dict[str, Any]],
        parameters: dict[str, dict[str, Any]],
        floor_name: str | None = None,
        room_name: str | None = None,
    ) -> None:
        """Initialize the Free@Home ForceOnOffSensor class."""
        self._state: ForceOnOffSensorState = ForceOnOffSensorState.unknown

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
        """Get the forceOnOff state."""
        return self._state.name

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
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
