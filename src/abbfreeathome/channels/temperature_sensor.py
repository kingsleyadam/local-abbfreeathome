"""Free@Home TemperatureSensor Class."""

from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class TemperatureSensor(Base):
    """Free@Home TemperatureSensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_OUTDOOR_TEMPERATURE,
        Pairing.AL_FROST_ALARM,
    ]
    _callback_attributes: list[str] = [
        "state",
        "alarm",
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
        """Initialize the Free@Home TemperatureSensor class."""
        self._state: float | None = None
        self._alarm: bool | None = None

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
    def state(self) -> float | None:
        """Get the temperature of the sensor."""
        return self._state

    @property
    def alarm(self) -> bool | None:
        """Get the alarm state of the sensor."""
        return self._alarm

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> bool:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if datapoint.get("pairingID") == Pairing.AL_OUTDOOR_TEMPERATURE.value:
            self._state = float(datapoint.get("value"))
            return "state"
        if datapoint.get("pairingID") == Pairing.AL_FROST_ALARM.value:
            self._alarm = datapoint.get("value") == "1"
            return "alarm"
        return None
