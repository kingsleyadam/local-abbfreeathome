"""Free@Home Virtual EnergyTwoWayMeter Class."""

from typing import TYPE_CHECKING, Any

from ...bin.pairing import Pairing
from ..base import Base

if TYPE_CHECKING:
    from ...device import Device


class VirtualEnergyTwoWayMeter(Base):
    """Free@Home Virtual EnergyTwoWayMeter Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_MEASURED_CURRENT_POWER_CONSUMED,
        Pairing.AL_MEASURED_IMPORTED_ENERGY_TODAY,
        Pairing.AL_MEASURED_EXPORTED_ENERGY_TODAY,
        Pairing.AL_MEASURED_TOTAL_ENERGY_IMPORTED,
        Pairing.AL_MEASURED_TOTAL_ENERGY_EXPORTED,
    ]
    _callback_attributes: list[str] = [
        "current_power",
        "imported_today",
        "exported_today",
        "imported_total",
        "exported_total",
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
        """Initialize the Free@Home Virtual EnergyTwoWayMeter class."""
        self._current_power: float | None = None
        self._imported_today: int | None = None
        self._exported_today: int | None = None
        self._imported_total: int | None = None
        self._exported_total: int | None = None

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
    def current_power(self) -> float | None:
        """Get the current consumed power of the sensor."""
        return self._current_power

    @property
    def imported_today(self) -> int | None:
        """Get the today imported energy of the sensor."""
        return self._imported_today

    @property
    def exported_today(self) -> int | None:
        """Get the today exported energy of the sensor."""
        return self._exported_today

    @property
    def imported_total(self) -> int | None:
        """Get the total exported energy of the sensor."""
        return self._imported_total

    @property
    def exported_total(self) -> int | None:
        """Get the total exported energy of the sensor."""
        return self._exported_total

    async def set_current_power(self, value: float):
        """Set current consumed power of the sensor."""
        await self._set_current_power_datapoint(str(value))
        self._current_power = value

    async def set_imported_today(self, value: int):
        """
        Set today imported energy of the sensor.

        The energy has to be greater or equal to 0.
        """
        value = int(max(0, value))
        await self._set_imported_today_datapoint(str(value))
        self._imported_today = value

    async def set_exported_today(self, value: int):
        """
        Set today exported energy of the sensor.

        The energy has to be greater or equal to 0.
        """
        value = int(max(0, value))
        await self._set_exported_today_datapoint(str(value))
        self._exported_today = value

    async def set_imported_total(self, value: int):
        """
        Set total imported energy of the sensor.

        The energy has to be greater or equal to 0.
        """
        value = int(max(0, value))
        await self._set_imported_total_datapoint(str(value))
        self._imported_total = value

    async def set_exported_total(self, value: int):
        """
        Set total exported energy of the sensor.

        The energy has to be greater or equal to 0.
        """
        value = int(max(0, value))
        await self._set_exported_total_datapoint(str(value))
        self._exported_total = value

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if (
            datapoint.get("pairingID")
            == Pairing.AL_MEASURED_CURRENT_POWER_CONSUMED.value
        ):
            try:
                self._current_power = float(datapoint.get("value"))
            except ValueError:
                self._current_power = 0.0
            return "current_power"
        if (
            datapoint.get("pairingID")
            == Pairing.AL_MEASURED_IMPORTED_ENERGY_TODAY.value
        ):
            try:
                self._imported_today = int(datapoint.get("value"))
            except ValueError:
                self._imported_today = 0
            return "imported_today"
        if (
            datapoint.get("pairingID")
            == Pairing.AL_MEASURED_EXPORTED_ENERGY_TODAY.value
        ):
            try:
                self._exported_today = int(datapoint.get("value"))
            except ValueError:
                self._exported_today = 0
            return "exported_today"
        if (
            datapoint.get("pairingID")
            == Pairing.AL_MEASURED_TOTAL_ENERGY_IMPORTED.value
        ):
            try:
                self._imported_total = int(datapoint.get("value"))
            except ValueError:
                self._imported_total = 0
            return "imported_total"
        if (
            datapoint.get("pairingID")
            == Pairing.AL_MEASURED_TOTAL_ENERGY_EXPORTED.value
        ):
            try:
                self._exported_total = int(datapoint.get("value"))
            except ValueError:
                self._exported_total = 0
            return "exported_total"

        return None

    async def _set_current_power_datapoint(self, value: str):
        """Set the sensor datapoint on the api."""
        _sensor_output_id, _sensor_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_MEASURED_CURRENT_POWER_CONSUMED
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_sensor_output_id,
            value=value,
        )

    async def _set_imported_today_datapoint(self, value: str):
        """Set the sensor datapoint on the api."""
        _sensor_output_id, _sensor_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_MEASURED_IMPORTED_ENERGY_TODAY
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_sensor_output_id,
            value=value,
        )

    async def _set_exported_today_datapoint(self, value: str):
        """Set the sensor datapoint on the api."""
        _sensor_output_id, _sensor_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_MEASURED_EXPORTED_ENERGY_TODAY
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_sensor_output_id,
            value=value,
        )

    async def _set_imported_total_datapoint(self, value: str):
        """Set the sensor datapoint on the api."""
        _sensor_output_id, _sensor_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_MEASURED_TOTAL_ENERGY_IMPORTED
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_sensor_output_id,
            value=value,
        )

    async def _set_exported_total_datapoint(self, value: str):
        """Set the sensor datapoint on the api."""
        _sensor_output_id, _sensor_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_MEASURED_TOTAL_ENERGY_EXPORTED
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_sensor_output_id,
            value=value,
        )
