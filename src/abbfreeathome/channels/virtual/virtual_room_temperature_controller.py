"""Free@Home Virtual RoomTemperatureController."""

import logging
from typing import TYPE_CHECKING, Any

from ...bin.pairing import Pairing
from ..base import Base

if TYPE_CHECKING:
    from ...device import Device

_LOGGER = logging.getLogger(__name__)


class VirtualRoomTemperatureController(Base):
    """Free@Home Virtual RoomTemperatureController Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_SET_POINT_TEMPERATURE,
        Pairing.AL_CONTROLLER_ON_OFF,
        Pairing.AL_STATE_INDICATION,
        Pairing.AL_MEASURED_TEMPERATURE,
    ]

    _input_refresh_pairings: list[Pairing] = [
        Pairing.AL_ECO_ON_OFF,
        Pairing.AL_CONTROLLER_ON_OFF_REQUEST,
        Pairing.AL_INFO_ABSOLUTE_SET_POINT_REQUEST,
    ]

    _callback_attributes: list[str] = [
        "state",
        "requested_state",
        "current_temperature",
        "target_temperature",
        "requested_target_temperature",
        "eco_mode",
        "requested_eco_mode",
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
        """Initialize the Free@Home Virtual RoomTemperatureController class."""
        self._state: bool | None = None
        self._requested_state: bool | None = None
        self._current_temperature: float | None = None
        self._target_temperature: float | None = None
        self._requested_target_temperature: float | None = None
        self._eco_mode: bool | None = None
        self._requested_eco_mode: bool | None = None

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
    def state(self) -> bool | None:
        """Get the state of the RTC."""
        return self._state

    @property
    def requested_state(self) -> bool | None:
        """Get the requested state of the RTC."""
        return self._requested_state

    @property
    def current_temperature(self) -> float | None:
        """Get the current temperature of the RTC."""
        return self._current_temperature

    @property
    def target_temperature(self) -> float | None:
        """Get the target temperature of the RTC."""
        return self._target_temperature

    @property
    def requested_target_temperature(self) -> float | None:
        """Get the requested target temperature of the RTC."""
        return self._requested_target_temperature

    @property
    def eco_mode(self) -> bool | None:
        """Get the eco mode of the RTC."""
        return self._eco_mode

    @property
    def requested_eco_mode(self) -> bool | None:
        """Get the requested eco mode of the RTC."""
        return self._requested_eco_mode

    async def turn_on(self):
        """Turn on the RTC."""
        await self._set_switching_datapoint("1")
        self._state = True

    async def turn_off(self):
        """Turn off the RTC."""
        await self._set_switching_datapoint("0")
        self._state = False

    async def turn_on_eco_mode(self):
        """Turn on the eco mode of the RTC."""
        await self._set_eco_datapoint("68")
        self._eco_mode = True

    async def turn_off_eco_mode(self):
        """Turn off the eco mode of the RTC."""
        await self._set_eco_datapoint("65")
        self._eco_mode = False

    async def set_target_temperature(self, value: float):
        """
        Set target temperature of the RTC.

        In F@H it is only possible to go down to 7°C and up to 35°C,
        so this is set as bounderies.
        """
        value = max(7, value)
        value = min(value, 35)

        await self._set_target_temperature_datapoint(str(value))
        self._target_temperature = value

    async def set_current_temperature(self, value: float):
        """Set current temperature of the RTC."""
        await self._set_current_temperature_datapoint(str(value))
        self._current_temperature = value

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:  # noqa: PLR0911
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if datapoint.get("pairingID") == Pairing.AL_ECO_ON_OFF.value:
            self._requested_eco_mode = datapoint.get("value") == "1"
            return "requested_eco_mode"
        if datapoint.get("pairingID") == Pairing.AL_STATE_INDICATION.value:
            self._eco_mode = int(datapoint.get("value")) & 0x04 == 0x04
            return "eco_mode"
        if datapoint.get("pairingID") == Pairing.AL_CONTROLLER_ON_OFF_REQUEST.value:
            self._requested_state = datapoint.get("value") == "1"
            return "requested_state"
        if datapoint.get("pairingID") == Pairing.AL_CONTROLLER_ON_OFF.value:
            self._state = datapoint.get("value") == "1"
            return "state"
        if (
            datapoint.get("pairingID")
            == Pairing.AL_INFO_ABSOLUTE_SET_POINT_REQUEST.value
        ):
            self._requested_target_temperature = float(datapoint.get("value"))
            return "requested_target_temperature"
        if datapoint.get("pairingID") == Pairing.AL_SET_POINT_TEMPERATURE.value:
            self._target_temperature = float(datapoint.get("value"))
            return "target_temperature"
        if datapoint.get("pairingID") == Pairing.AL_MEASURED_TEMPERATURE.value:
            self._current_temperature = float(datapoint.get("value"))
            return "current_temperature"
        return None

    async def _set_switching_datapoint(self, value: str):
        """Set the switching datapoint on the api."""
        _switch_output_id, _switch_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_CONTROLLER_ON_OFF
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_switch_output_id,
            value=value,
        )

    async def _set_eco_datapoint(self, value: str):
        """Set the eco datapoint on the api."""
        _eco_output_id, _eco_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_STATE_INDICATION
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_eco_output_id,
            value=value,
        )

    async def _set_target_temperature_datapoint(self, value: str):
        """Set the target temperature datapoint on the api."""
        _temp_output_id, _temp_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_SET_POINT_TEMPERATURE
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_temp_output_id,
            value=value,
        )

    async def _set_current_temperature_datapoint(self, value: str):
        """Set the current temperature datapoint on the api."""
        _temp_output_id, _temp_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_MEASURED_TEMPERATURE
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_temp_output_id,
            value=value,
        )

    def update_channel(self, datapoint_key: str, datapoint_value: str):
        """Update the channel state."""
        _LOGGER.info(
            "%s received updated data: %s: %s",
            self.channel_name,
            datapoint_key,
            datapoint_value,
        )

        _callback_attribute = None
        _io_key = datapoint_key.split("/")[-1]

        if _io_key in self._outputs:
            self._outputs[_io_key]["value"] = datapoint_value
            _callback_attribute = self._refresh_state_from_datapoint(
                datapoint=self._outputs[_io_key]
            )

        if _io_key in self._inputs:
            self._inputs[_io_key]["value"] = datapoint_value
            _callback_attribute = self._refresh_state_from_datapoint(
                datapoint=self._inputs[_io_key]
            )

        if _callback_attribute and self._callbacks[_callback_attribute]:
            for callback in self._callbacks[_callback_attribute]:
                callback()
