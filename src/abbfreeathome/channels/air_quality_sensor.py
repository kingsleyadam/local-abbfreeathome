"""Free@Home AirQualitySensor Class."""

from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class AirQualitySensor(Base):
    """Free@Home AirQualitySensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_CO_2,
        Pairing.AL_CO2_ALERT,
        Pairing.AL_INFO_VOC_INDEX,
        Pairing.AL_VOC_ALERT,
        Pairing.AL_HUMIDITY,
    ]
    _callback_attributes: list[str] = [
        "co2",
        "co2_alert",
        "voc_index",
        "voc_alert",
        "humidity",
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
        """Initialize the Free@Home AirQualitySensor class."""
        self._co2: float | None = None
        self._co2_alert: bool | None = None
        self._voc_index: int | None = None
        self._voc_alert: bool | None = None
        self._humidity: int | None = None

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
    def co2(self) -> float | None:
        """Get the CO2 concentration in ppm."""
        return self._co2

    @property
    def co2_alert(self) -> bool | None:
        """Get the CO2 alert status."""
        return self._co2_alert

    @property
    def voc_index(self) -> int | None:
        """Get the VOC (Volatile Organic Compounds) index."""
        return self._voc_index

    @property
    def voc_alert(self) -> bool | None:
        """Get the VOC alert status."""
        return self._voc_alert

    @property
    def humidity(self) -> int | None:
        """Get the humidity percentage."""
        return self._humidity

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        pairing_id = datapoint.get("pairingID")
        value = datapoint.get("value")

        if pairing_id == Pairing.AL_INFO_CO_2.value:
            self._co2 = float(value)
            return "co2"
        if pairing_id == Pairing.AL_CO2_ALERT.value:
            self._co2_alert = value == "1"
            return "co2_alert"
        if pairing_id == Pairing.AL_INFO_VOC_INDEX.value:
            self._voc_index = int(value)
            return "voc_index"
        if pairing_id == Pairing.AL_VOC_ALERT.value:
            self._voc_alert = value == "1"
            return "voc_alert"
        if pairing_id == Pairing.AL_HUMIDITY.value:
            self._humidity = int(value)
            return "humidity"
        return None
