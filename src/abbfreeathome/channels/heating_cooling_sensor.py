"""Free@Home HeatingCoolingSensor Class."""

import enum
import logging
from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device

_LOGGER = logging.getLogger(__name__)


class HeatingCoolingSensorState(enum.Enum):
    """
    Heating/cooling changeover states defined by AL_HEATING_COOLING.

    The ABB SDK comments heating = 0 / cooling = 1, but room temperature
    controllers on real systems heat at 1 and cool at 0, so follow the hardware:
    https://github.com/Busch-Jaeger/node-free-at-home/blob/master/src/pairingIds.ts
    https://github.com/kingsleyadam/local-abbfreeathome-hass/issues/397
    """

    unknown = None
    heating = "1"
    cooling = "0"


class HeatingCoolingSensor(Base):
    """Free@Home heating/cooling changeover sensor."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_HEATING_COOLING,
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
        """Initialize the Free@Home HeatingCoolingSensor class."""
        self._state: HeatingCoolingSensorState = HeatingCoolingSensorState.unknown

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
        """Get the heating/cooling mode, or unknown for missing or invalid data."""
        return self._state.name

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> list[str]:
        """Refresh state and return the affected attribute names."""
        if datapoint.get("pairingID") == Pairing.AL_HEATING_COOLING.value:
            value = datapoint.get("value")
            if value in ("0", "1"):
                self._state = HeatingCoolingSensorState(value)
            else:
                self._state = HeatingCoolingSensorState.unknown
                _LOGGER.warning(
                    "Invalid heating/cooling value %r for %s",
                    value,
                    self.channel_name,
                )
            return ["state"]
        return []
