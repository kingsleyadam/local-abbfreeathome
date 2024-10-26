"""Free@Home RainSensor Class."""

# I added also the other two output-datapoint, but I let them deacticated.
# I just don't know when they get changed

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class RainSensor(Base):
    """Free@Home RainSensor Class."""

    _state_refresh_output_pairings: list[Pairing] = [
        Pairing.AL_RAIN_ALARM,
        # Pairing.AL_RAIN_SENSOR_ACTIVATION_PERCENTAGE,
        # Pairing.AL_RAIN_SENSOR_FREQUENCY,
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
        """Initialize the Free@Home RainSensor class."""
        self._state: bool | None = None
        # self._percentage: float | None = None
        # self._frequency: float | None = None

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
        """Get the rain alarm of the sensor."""
        return self._state

    # @property
    # def percentage(self) -> float | None:
    #    """Get the percentage of the sensor."""
    #    return self._alarm

    # @property
    # def frequency(self) -> float | None:
    #    """Get the frequency of the sensor."""
    #    return self._frequency

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_RAIN_ALARM.value:
            self._state = output.get("value") == "1"
            return True
        # if output.get("pairingID") == Pairing.AL_RAIN_SENSOR_ACTIVATION_PERCENTAGE.value:  # noqa: E501
        #    self._percentage = float(output.get("value"))
        #    return True
        # if output.get("pairingID") == Pairing.AL_RAIN_SENSOR_FREQUENCY.value:
        #    self._frequency = float(output.get("value"))
        #    return True
        return False
