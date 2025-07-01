"""Free@Home Virtual WindSensor Class."""

from typing import TYPE_CHECKING, Any

from ...bin.pairing import Pairing
from ..base import Base

if TYPE_CHECKING:
    from ...device import Device


class VirtualWindSensor(Base):
    """Free@Home Virtual WindSensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_WIND_SPEED,
        Pairing.AL_WIND_ALARM,
        Pairing.AL_WIND_FORCE,
    ]
    _callback_attributes: list[str] = [
        "speed",
        "alarm",
        "force",
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
        """Initialize the Free@Home Virtual WindSensor class."""
        self._speed: float | None = None
        self._alarm: bool | None = None
        self._force: int | None = None

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
    def speed(self) -> float | None:
        """Get the speed of the sensor."""
        return self._speed

    @property
    def alarm(self) -> bool | None:
        """Get the alarm state of the sensor."""
        return self._alarm

    @property
    def force(self) -> int | None:
        """Get the force of the sensor."""
        return self._force

    async def set_speed(self, value: float):
        """
        Set speed of the sensor.

        The speed has to be greater or equal to 0.
        """

        value = max(0, value)
        await self._set_speed_datapoint(str(value))
        self._speed = value

    async def turn_on(self):
        """Turn on the wind alarm."""
        await self._set_alarm_datapoint("1")
        self._alarm = True

    async def turn_off(self):
        """Turn off the wind alarm."""
        await self._set_alarm_datapoint("0")
        self._alarm = False

    async def set_force(self, value: int):
        """
        Set force of the sensor.

        The force has to be between 0 and 12 (beaufort)
        """
        value = int(value)
        value = max(0, value)
        value = min(value, 12)

        await self._set_force_datapoint(str(value))
        self._force = value

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if datapoint.get("pairingID") == Pairing.AL_WIND_SPEED.value:
            try:
                self._speed = float(datapoint.get("value"))
            except ValueError:
                self._speed = 0.0
            return "speed"
        if datapoint.get("pairingID") == Pairing.AL_WIND_ALARM.value:
            self._alarm = datapoint.get("value") == "1"
            return "alarm"
        if datapoint.get("pairingID") == Pairing.AL_WIND_FORCE.value:
            try:
                self._force = int(datapoint.get("value"))
            except ValueError:
                self._force = 0
            return "force"

        return None

    async def _set_speed_datapoint(self, value: str):
        """Set the sensor datapoint on the api."""
        _sensor_output_id, _sensor_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_WIND_SPEED
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_sensor_output_id,
            value=value,
        )

    async def _set_alarm_datapoint(self, value: str):
        """Set the sensor datapoint on the api."""
        _sensor_output_id, _sensor_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_WIND_ALARM
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_sensor_output_id,
            value=value,
        )

    async def _set_force_datapoint(self, value: str):
        """Set the sensor datapoint on the api."""
        _sensor_output_id, _sensor_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_WIND_FORCE
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_sensor_output_id,
            value=value,
        )
