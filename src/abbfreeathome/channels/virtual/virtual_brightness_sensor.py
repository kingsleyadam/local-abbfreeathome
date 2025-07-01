"""Free@Home Virtual BrightnessSensor Class."""

from typing import TYPE_CHECKING, Any

from ...bin.pairing import Pairing
from ..base import Base

if TYPE_CHECKING:
    from ...device import Device


class VirtualBrightnessSensor(Base):
    """Free@Home Virtual BrightnessSensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_BRIGHTNESS_LEVEL,
        Pairing.AL_BRIGHTNESS_ALARM,
    ]
    _callback_attributes: list[str] = [
        "brightness",
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
        """Initialize the Free@Home Virtual BrightnessSensor class."""
        self._brightness: int | None = None
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
    def brightness(self) -> int | None:
        """Get the brightness level of the sensor."""
        return self._brightness

    @property
    def alarm(self) -> bool | None:
        """Get the alarm state of the sensor."""
        return self._alarm

    async def set_brightness(self, value: int):
        """
        Set brightness level of the sensor.

        The brightness has to be greater or equal to 0.
        """

        value = int(max(0, value))
        await self._set_brightness_datapoint(str(value))
        self._brightness = value

    async def turn_on(self):
        """Turn on the brightness alarm."""
        await self._set_alarm_datapoint("1")
        self._alarm = True

    async def turn_off(self):
        """Turn off the brightness alarm."""
        await self._set_alarm_datapoint("0")
        self._alarm = False

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if datapoint.get("pairingID") == Pairing.AL_BRIGHTNESS_LEVEL.value:
            try:
                self._brightness = int(float(datapoint.get("value")))
            except ValueError:
                self._brightness = 0
            return "brightness"
        if datapoint.get("pairingID") == Pairing.AL_BRIGHTNESS_ALARM.value:
            self._alarm = datapoint.get("value") == "1"
            return "alarm"

        return None

    async def _set_brightness_datapoint(self, value: str):
        """Set the sensor datapoint on the api."""
        _sensor_output_id, _sensor_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_BRIGHTNESS_LEVEL
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
            pairing=Pairing.AL_BRIGHTNESS_ALARM
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_sensor_output_id,
            value=value,
        )
