"""Free@Home HeatingCoolingSensor Class."""

import logging
from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device

_LOGGER = logging.getLogger(__name__)


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
        self._state: bool | None = None

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
        """
        Get the raw changeover signal, with "1" represented as True.

        Missing or invalid values are represented as None.
        The heating/cooling meaning of this signal is not yet confirmed.
        """
        return self._state

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> list[str]:
        """Refresh state and return the affected attribute names."""
        if datapoint.get("pairingID") == Pairing.AL_HEATING_COOLING.value:
            value = datapoint.get("value")
            if value in ("0", "1"):
                self._state = value == "1"
            else:
                self._state = None
                _LOGGER.warning(
                    "Invalid heating/cooling value %r for %s",
                    value,
                    self.channel_name,
                )
            return ["state"]
        return []
