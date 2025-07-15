"""Free@Home DimmingActuator Class."""

import enum
from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from ..bin.parameter import Parameter
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class DimmingActuatorForcedPosition(enum.Enum):
    """An Enum class for the force states."""

    unknown = None
    deactivated = "0"
    forced_on = "4"
    forced_off = "5"


class DimmingActuator(Base):
    """Free@Home DimmingActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_FORCE,
        Pairing.AL_INFO_ON_OFF,
        Pairing.AL_INFO_ACTUAL_DIMMING_VALUE,
    ]
    _callback_attributes: list[str] = [
        "state",
        "brightness",
        "forced_position",
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
        """Initialize the Free@Home DimmingActuator class."""
        self._state: bool | None = None
        self._brightness: int | None = None
        self._forced_position: DimmingActuatorForcedPosition = (
            DimmingActuatorForcedPosition.unknown
        )

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
    def state(self) -> bool:
        """Get the state of the dimming actuator."""
        return bool(self._state)

    @property
    def brightness(self) -> int:
        """Get the brightness level of the dimmer."""
        return int(self._brightness)

    @property
    def forced_position(self) -> str | None:
        """Get the forced state of the dimmer."""
        return self._forced_position.name

    async def turn_on(self):
        """Turn on the dimmer."""
        await self._set_switching_datapoint("1")
        self._state = True

    async def turn_off(self):
        """Turn on the dimmer."""
        await self._set_switching_datapoint("0")
        self._state = False

    async def set_brightness(self, value: int):
        """
        Set the brightness of the dimmer.

        The brightness has to be between 1 and 100
        """

        value = max(1, value)
        value = min(value, 100)

        await self._set_brightness_datapoint(str(value))
        self._brightness = value

    async def set_forced_position(self, forced_position_name: str):
        """Set the forced-option on the dimmer."""
        try:
            _position = DimmingActuatorForcedPosition[forced_position_name]
        except KeyError:
            _position = DimmingActuatorForcedPosition.unknown

        if _position == DimmingActuatorForcedPosition.deactivated:
            await self._set_forced_datapoint("0")
        if _position == DimmingActuatorForcedPosition.forced_on:
            await self._set_forced_datapoint("3")
        if _position == DimmingActuatorForcedPosition.forced_off:
            await self._set_forced_datapoint("2")

        self._forced_position = _position

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if datapoint.get("pairingID") == Pairing.AL_INFO_ON_OFF.value:
            self._state = datapoint.get("value") == "1"
            return "state"
        if datapoint.get("pairingID") == Pairing.AL_INFO_ACTUAL_DIMMING_VALUE.value:
            self._brightness = int(float(datapoint.get("value")))
            return "brightness"
        if datapoint.get("pairingID") == Pairing.AL_INFO_FORCE.value:
            try:
                self._forced_position = DimmingActuatorForcedPosition(
                    datapoint.get("value")
                )
            except ValueError:
                self._forced_position = DimmingActuatorForcedPosition.unknown
            return "forced_position"
        return None

    async def _set_switching_datapoint(self, value: str):
        """Set the switching datapoint on the api."""
        _switch_input_id, _switch_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_SWITCH_ON_OFF
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_switch_input_id,
            value=value,
        )

    async def _set_brightness_datapoint(self, value: str):
        """Set the brightness datapoint on the api."""
        _brightness_input_id, _brightness_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_ABSOLUTE_SET_VALUE_CONTROL
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_brightness_input_id,
            value=value,
        )

    async def _set_forced_datapoint(self, value: str):
        """Set the force datapoint on the api."""
        _force_input_id, _force_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_FORCED
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_force_input_id,
            value=value,
        )


class ColorTemperatureActuator(DimmingActuator):
    """Free@Home ColorTemperatureActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_FORCE,
        Pairing.AL_INFO_ON_OFF,
        Pairing.AL_INFO_ACTUAL_DIMMING_VALUE,
        Pairing.AL_INFO_COLOR_TEMPERATURE,
    ]
    _callback_attributes: list[str] = [
        "state",
        "brightness",
        "forced_position",
        "color_temperature",
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
        """Initialize the Free@Home ColorTemperatureActuator class."""
        self._color_temperature: int | None = None

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
    def color_temperature_coolest(self) -> int | None:
        """Get the coolest color temperature of the light."""
        _id, _value = self.get_channel_parameter(
            parameter=Parameter.PID_TEMPERATURE_COLOR_PHYSICAL_COOLEST
        )
        return int(_value)

    @property
    def color_temperature_warmest(self) -> int | None:
        """Get the warmest color temperature of the light."""
        _id, _value = self.get_channel_parameter(
            parameter=Parameter.PID_TEMPERATURE_COLOR_PHYSICAL_WARMEST
        )
        return int(_value)

    @property
    def color_temperature(self) -> int | None:
        """Get the color temperature of the light."""
        return self._color_temperature

    async def set_color_temperature(self, value: int):
        """
        Set the color temperature of the light.

        The color temperature has to be between 0 and 100
        0 is the warmest setting
        100 is the coolest setting
        Just as an information: HA uses Kelvin to define the color temperature,
        so in HA we need to transform Kelvin to this value-range.
        """
        value = max(0, value)
        value = min(value, 100)
        await self._set_color_temperature_datapoint(str(value))
        self._color_temperature = value

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if datapoint.get("pairingID") == Pairing.AL_INFO_COLOR_TEMPERATURE.value:
            self._color_temperature = int(float(datapoint.get("value")))
            return "color_temperature"
        return super()._refresh_state_from_datapoint(datapoint)

    async def _set_color_temperature_datapoint(self, value: str):
        """Set the color temperature on the api."""
        _color_temp_id, _color_temp_value = self.get_input_by_pairing(
            pairing=Pairing.AL_COLOR_TEMPERATURE
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_color_temp_id,
            value=value,
        )
