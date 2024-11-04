"""Free@Home RoomTemperatureController Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class RoomTemperatureController(Base):
    """Free@Home RoomTemperatureController Class."""

    _state_refresh_output_pairings: list[Pairing] = [
        Pairing.AL_SET_POINT_TEMPERATURE,
        Pairing.AL_STATE_INDICATION,
        Pairing.AL_MEASURED_TEMPERATURE,
        Pairing.AL_HEATING_DEMAND,
        Pairing.AL_CONTROLLER_ON_OFF,
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
        """Initialize the Free@Home RoomTemperatureController class."""
        self._state: bool | None = None
        self._current_temperature: float | None = None
        self._valve: int | None = None
        self._target_temperature: float | None = None
        self._state_indication: int | None = None
        self._eco_mode: bool | None = None

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
    def state(self) -> bool:
        """Get the state of the RTC."""
        return bool(self._state)

    @property
    def current_temperature(self) -> float | None:
        """Get the current temperature."""
        return self._current_temperature

    @property
    def valve(self) -> int | None:
        """Get the status of the valve."""
        return self._valve

    @property
    def target_temperature(self) -> float | None:
        """Get the target temperature."""
        return self._target_temperature

    @property
    def state_indication(self) -> int | None:
        """Get the state indication."""
        return self._state_indication

    @property
    def eco_mode(self) -> bool | None:
        """Get the state of the eco_mode."""
        return self._eco_mode

    async def turn_on(self):
        """Turn on the RTC."""
        await self._set_switching_datapoint("1")
        self._state = True

    async def turn_off(self):
        """Turn off the RTC."""
        await self._set_switching_datapoint("0")
        self._state = False

    async def eco_on(self):
        """Turn on eco-mode."""
        await self._set_eco_datapoint("1")
        self._eco_mode = True

    async def eco_off(self):
        """Turn off eco-mode."""
        await self._set_eco_datapoint("0")
        self._eco_mode = False

    async def set_temperature(self, value: float):
        """
        Set target temperature of RTC.

        In F@H it is only possible to go down to 7°C and up to 35°C,
        so this is set as boundaries.
        """
        value = max(7, value)
        value = min(value, 35)

        await self._set_temperature_datapoint(str(value))
        self._target_temperature = value

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_SET_POINT_TEMPERATURE.value:
            self._target_temperature = float(output.get("value"))
            return True
        if output.get("pairingID") == Pairing.AL_CONTROLLER_ON_OFF.value:
            self._state = output.get("value") == "1"
            return True
        if output.get("pairingID") == Pairing.AL_STATE_INDICATION.value:
            """
            This returns a integer bitwise-ORed with the following masks:
            0x01 - comfort mode                 (65)
            0x02 - standby
            0x04 - eco mode                     (68)
            0x08 - building protect
            0x10 - dew alarm
            0x20 - heat (set) / cool (unset)    (33)
            0x40 - no heating/cooling (set)
            0x80 - frost alarm

            At the moment only 0x04 (eco mode) is needed
            """
            self._state_indication = int(output.get("value"))
            self._eco_mode = int(output.get("value")) & 0x04 == 0x04
            return True
        if output.get("pairingID") == Pairing.AL_MEASURED_TEMPERATURE.value:
            self._current_temperature = float(output.get("value"))
            return True
        if output.get("pairingID") == Pairing.AL_HEATING_DEMAND.value:
            try:
                self._valve = int(output.get("value"))
            except ValueError:
                self._valve = None
            return True
        return False

    async def _set_switching_datapoint(self, value: str):
        """Set the switching datapoint on the api."""
        _switch_input_id, _switch_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_CONTROLLER_ON_OFF_REQUEST
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_switch_input_id,
            value=value,
        )

    async def _set_eco_datapoint(self, value: str):
        """Set the eco-mode datapoint on the api."""
        _eco_input_id, _eco_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_ECO_ON_OFF
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_eco_input_id,
            value=value,
        )

    async def _set_temperature_datapoint(self, value: str):
        """Set the target temperature datapoint on the api."""
        _temperature_input_id, _temperature_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_INFO_ABSOLUTE_SET_POINT_REQUEST
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_temperature_input_id,
            value=value,
        )
