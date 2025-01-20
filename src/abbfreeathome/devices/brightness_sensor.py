"""Free@Home BrightnessSensor Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .real_base import RealBase


class BrightnessSensor(RealBase):
    """Free@Home BrightnessSensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_BRIGHTNESS_LEVEL,
        Pairing.AL_BRIGHTNESS_ALARM,
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
        """Initialize the Free@Home BrightnessSensor class."""
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
        """Get the brightness level of the sensor."""
        return self._state

    @property
    def alarm(self) -> bool | None:
        """Get the alarm state of the sensor."""
        return self._alarm

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if datapoint.get("pairingID") == Pairing.AL_BRIGHTNESS_LEVEL.value:
            self._state = float(datapoint.get("value"))
            return True
        if datapoint.get("pairingID") == Pairing.AL_BRIGHTNESS_ALARM.value:
            self._alarm = datapoint.get("value") == "1"
            return True
        return False
