"""Free@Home TemperatureSensor Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class TemperatureSensor(Base):
    """Free@Home TemperatureSensor Class."""

    _state_refresh_output_pairings: list[Pairing] = [
        Pairing.AL_OUTDOOR_TEMPERATURE,
        Pairing.AL_FROST_ALARM,
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
        """Initialize the Free@Home TemperatureSensor class."""
        self._state: float | None = None
        self._alarm: bool | None = None

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
    def state(self) -> float | None:
        """Get the temperature of the sensor."""
        return self._state

    @property
    def alarm(self) -> bool | None:
        """Get the alarm state of the sensor."""
        return self._alarm

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_OUTDOOR_TEMPERATURE.value:
            self._state = float(output.get("value"))
            return True
        if output.get("pairingID") == Pairing.AL_FROST_ALARM.value:
            self._alarm = output.get("value") == "1"
            return True
        return False
