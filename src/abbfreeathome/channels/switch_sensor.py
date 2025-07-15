"""Free@Home SwitchSensor Class."""

import enum
from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from ..bin.parameter import Parameter
from ..exceptions import InvalidDeviceChannelParameter
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class SwitchSensorState(enum.Enum):
    """An Enum class for the switch sensor states."""

    unknown = None
    off = "0"
    on = "1"


class DimmingSensorState(enum.Enum):
    """An Enum class for the dimming sensor states."""

    unknown = None
    longpress_up = "9"
    longpress_up_release = "8"
    longpress_down = "1"
    longpress_down_release = "0"


class SwitchSensor(Base):
    """Free@Home SwitchSensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_SWITCH_ON_OFF,
    ]
    _input_state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_ON_OFF,
    ]
    _callback_attributes: list[str] = [
        "state",
        "led",
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
        """Initialize the Free@Home SwitchSensor class."""
        self._state: SwitchSensorState | DimmingSensorState = SwitchSensorState.unknown
        self._switch_sensor_state: SwitchSensorState = SwitchSensorState.unknown
        self._led: bool | None = None

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
    def state(self) -> str:
        """Get the state."""
        return self._state.name

    @property
    def switching_state(self) -> str:
        """Get the switch state."""
        return self._switch_sensor_state.name

    @property
    def led(self) -> bool | None:
        """Get the led-state of the sensor."""
        return self._led

    async def turn_on_led(self):
        """Turn on the led of the sensor."""
        await self._set_led_datapoint("1")
        self._led = True

    async def turn_off_led(self):
        """Turn off the led of the sensor."""
        await self._set_led_datapoint("0")
        self._led = False

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if datapoint.get("pairingID") == Pairing.AL_SWITCH_ON_OFF.value:
            try:
                self._switch_sensor_state = SwitchSensorState(datapoint.get("value"))
            except ValueError:
                self._switch_sensor_state = SwitchSensorState.unknown

            self._state = self._switch_sensor_state
            return "state"
        if datapoint.get("pairingID") == Pairing.AL_INFO_ON_OFF.value:
            try:
                _, _parameter_value = self.get_channel_parameter(
                    parameter=Parameter.PID_LED_OPERATION_MODE
                )
                if _parameter_value == "2":
                    self._led = datapoint.get("value") == "1"
                    return "led"
            except InvalidDeviceChannelParameter:
                return None
        return None

    async def _set_led_datapoint(self, value: str):
        """Set the led datapoint on the api."""
        _sensor_input_id, _sensor_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_INFO_ON_OFF
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_sensor_input_id,
            value=value,
        )

    def update_channel(self, datapoint_key, datapoint_value):
        """Update the channel state."""
        super().update_channel(datapoint_key, datapoint_value)
        _callback_attribute = None
        _io_key = datapoint_key.split("/")[-1]

        if _io_key in self._inputs:
            self._inputs[_io_key]["value"] = datapoint_value
            _callback_attribute = self._refresh_state_from_datapoint(
                datapoint=self._inputs[_io_key]
            )

        if _callback_attribute and self._callbacks[_callback_attribute]:
            for callback in self._callbacks[_callback_attribute]:
                callback()

    async def refresh_state(self):
        """Refresh the state of the channel from the api."""
        await super().refresh_state()

        for _pairing in self._input_state_refresh_pairings:
            _datapoint_id, _datapoint_value = self.get_input_by_pairing(
                pairing=_pairing
            )

            _datapoint = (
                await self.device.api.get_datapoint(
                    device_serial=self.device_serial,
                    channel_id=self.channel_id,
                    datapoint=_datapoint_id,
                )
            )[0]

            self._refresh_state_from_datapoint(
                datapoint={
                    "pairingID": _pairing.value,
                    "value": _datapoint,
                }
            )

    def _refresh_state_from_datapoints(self):
        """Refresh the state of the channel from the datapoints."""
        super()._refresh_state_from_datapoints()

        for _datapoint in self._inputs.values():
            self._refresh_state_from_datapoint(_datapoint)


class DimmingSensor(SwitchSensor):
    """Free@Home DimmingSensor Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_RELATIVE_SET_VALUE_CONTROL,
        Pairing.AL_SWITCH_ON_OFF,
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
        """Initialize the Free@Home DimmingSensor class."""
        self._state: SwitchSensorState | DimmingSensorState = SwitchSensorState.unknown
        self._dimming_sensor_state: DimmingSensorState = DimmingSensorState.unknown

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
    def dimming_state(self) -> str:
        """Get the dimming state."""
        return self._dimming_sensor_state.name

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        _return_value = super()._refresh_state_from_datapoint(datapoint)
        if _return_value is not None:
            return _return_value

        if datapoint.get("pairingID") == Pairing.AL_RELATIVE_SET_VALUE_CONTROL.value:
            try:
                self._dimming_sensor_state = DimmingSensorState(datapoint.get("value"))
            except ValueError:
                self._dimming_sensor_state = DimmingSensorState.unknown

            self._state = self._dimming_sensor_state
            return "state"
        return None
