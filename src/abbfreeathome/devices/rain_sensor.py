"""Free@Home RainSensor Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class RainSensor(Base):
    """Free@Home RainSensor Class."""

    _state_refresh_output_pairings: list[Pairing] = [
        Pairing.AL_RAIN_ALARM,
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
        virtual_device: bool = False,
    ) -> None:
        """Initialize the Free@Home RainSensor class."""
        self._state: bool | None = None

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
            virtual_device,
        )

    @property
    def state(self) -> bool | None:
        """Get the rain alarm of the sensor."""
        return self._state

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_RAIN_ALARM.value:
            self._state = output.get("value") == "1"
            return True
        return False
