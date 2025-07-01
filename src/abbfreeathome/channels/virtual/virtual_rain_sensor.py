"""Free@Home Virtual RainSensor Class."""

from typing import TYPE_CHECKING, Any

from ...bin.pairing import Pairing
from ..base import Base

if TYPE_CHECKING:
    from ...device import Device


class VirtualRainSensor(Base):
    """Free@Home Virtual RainSensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_RAIN_ALARM,
    ]
    _callback_attributes: list[str] = [
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
        """Initialize the Free@Home Virtual RainSensor class."""
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
    def alarm(self) -> bool | None:
        """Get the alarm state of the sensor."""
        return self._alarm

    async def turn_on(self):
        """Turn on the wind alarm."""
        await self._set_alarm_datapoint("1")
        self._alarm = True

    async def turn_off(self):
        """Turn off the wind alarm."""
        await self._set_alarm_datapoint("0")
        self._alarm = False

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if datapoint.get("pairingID") == Pairing.AL_RAIN_ALARM.value:
            self._alarm = datapoint.get("value") == "1"
            return "alarm"

        return None

    async def _set_alarm_datapoint(self, value: str):
        """Set the sensor datapoint on the api."""
        _sensor_output_id, _sensor_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_RAIN_ALARM
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_sensor_output_id,
            value=value,
        )
