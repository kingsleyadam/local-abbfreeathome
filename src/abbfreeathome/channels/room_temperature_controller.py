"""Free@Home RoomTemperatureController Class."""

from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class RoomTemperatureController(Base):
    """Free@Home RoomTemperatureController Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_SET_POINT_TEMPERATURE,
        Pairing.AL_STATE_INDICATION,
        Pairing.AL_MEASURED_TEMPERATURE,
        Pairing.AL_ACTUATING_VALUE_HEATING,
        Pairing.AL_ACTUATING_VALUE_COOLING,
        Pairing.AL_CONTROLLER_ON_OFF,
    ]
    _callback_attributes: list[str] = [
        "state",
        "current_temperature",
        "heating",
        "cooling",
        "target_temperature",
        "state_indication",
        "eco_mode",
        "heating_mode",
        "heating_cooling_active",
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
        """Initialize the Free@Home RoomTemperatureController class."""
        self._state: bool | None = None
        self._current_temperature: float | None = None
        self._heating: int | None = 0
        self._cooling: int | None = 0
        self._target_temperature: float | None = None
        self._state_indication: int | None = None
        self._eco_mode: bool | None = None

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
        """Get the state of the RTC."""
        return bool(self._state)

    @property
    def current_temperature(self) -> float | None:
        """Get the current temperature."""
        return self._current_temperature

    @property
    def heating(self) -> int | None:
        """Get the status of the heating."""
        return self._heating

    @property
    def cooling(self) -> int | None:
        """Get the status of the cooling."""
        return self._cooling

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

    @property
    def heating_mode(self) -> bool | None:
        """Get the indicated mode: True for heating, False for cooling."""
        if self._state_indication is None:
            return None
        return bool(self._state_indication & 0x20)

    @property
    def heating_cooling_active(self) -> bool | None:
        """Get whether the indication allows heating/cooling rather than idle."""
        if self._state_indication is None:
            return None
        return not bool(self._state_indication & 0x40)

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

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> list[str]:  # noqa: PLR0911
        """
        Refresh the state of the channel from a given output.

        Return the names of the attributes refreshed by this datapoint.
        """
        if datapoint.get("pairingID") == Pairing.AL_SET_POINT_TEMPERATURE.value:
            self._target_temperature = float(datapoint.get("value"))
            return ["target_temperature"]
        if datapoint.get("pairingID") == Pairing.AL_CONTROLLER_ON_OFF.value:
            self._state = datapoint.get("value") == "1"
            return ["state"]
        if datapoint.get("pairingID") == Pairing.AL_STATE_INDICATION.value:
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
            """
            self._state_indication = int(datapoint.get("value"))
            self._eco_mode = self._state_indication & 0x04 == 0x04
            return [
                "state_indication",
                "eco_mode",
                "heating_mode",
                "heating_cooling_active",
            ]
        if datapoint.get("pairingID") == Pairing.AL_MEASURED_TEMPERATURE.value:
            self._current_temperature = float(datapoint.get("value"))
            return ["current_temperature"]
        if datapoint.get("pairingID") == Pairing.AL_ACTUATING_VALUE_HEATING.value:
            try:
                self._heating = int(float(datapoint.get("value")))
            except ValueError:
                self._heating = 0
            return ["heating"]
        if datapoint.get("pairingID") == Pairing.AL_ACTUATING_VALUE_COOLING.value:
            try:
                self._cooling = int(float(datapoint.get("value")))
            except ValueError:
                self._cooling = 0
            return ["cooling"]
        return []

    async def _set_switching_datapoint(self, value: str):
        """Set the switching datapoint on the api."""
        _switch_input_id, _switch_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_CONTROLLER_ON_OFF_REQUEST
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_switch_input_id,
            value=value,
        )

    async def _set_eco_datapoint(self, value: str):
        """Set the eco-mode datapoint on the api."""
        _eco_input_id, _eco_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_ECO_ON_OFF
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_eco_input_id,
            value=value,
        )

    async def _set_temperature_datapoint(self, value: str):
        """Set the target temperature datapoint on the api."""
        _temperature_input_id, _temperature_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_INFO_ABSOLUTE_SET_POINT_REQUEST
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_temperature_input_id,
            value=value,
        )


class RadiatorActuator(RoomTemperatureController):
    """
    Free@Home RadiatorActuator Class.

    A radiator thermostat carries the same datapoints as a room temperature
    controller, except for the heating state: it reports AL_HEATING_ACTIVE and
    AL_HEATING_DEMAND instead of AL_ACTUATING_VALUE_HEATING and
    AL_ACTUATING_VALUE_COOLING, and it does not cool at all.
    """

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_SET_POINT_TEMPERATURE,
        Pairing.AL_STATE_INDICATION,
        Pairing.AL_MEASURED_TEMPERATURE,
        Pairing.AL_CONTROLLER_ON_OFF,
        Pairing.AL_HEATING_ACTIVE,
        Pairing.AL_HEATING_DEMAND,
    ]
    _callback_attributes: list[str] = [
        "state",
        "current_temperature",
        "heating",
        "cooling",
        "target_temperature",
        "state_indication",
        "eco_mode",
        "heating_mode",
        "heating_cooling_active",
        "heating_active",
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
        """Initialize the Free@Home RadiatorActuator class."""
        self._heating_active: bool = False

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
    def heating_active(self) -> bool:
        """
        Get whether the radiator is currently heating.

        Falls back to the heating demand for thermostats that report a demand
        without setting the active flag.
        """
        return self._heating_active or bool(self._heating)

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> list[str]:
        """
        Refresh the state of the channel from a given output.

        Return the names of the attributes refreshed by this datapoint.
        """
        if datapoint.get("pairingID") == Pairing.AL_HEATING_ACTIVE.value:
            self._heating_active = datapoint.get("value") == "1"
            return ["heating_active"]
        if datapoint.get("pairingID") == Pairing.AL_HEATING_DEMAND.value:
            was_heating_active = self.heating_active
            try:
                self._heating = int(float(datapoint.get("value")))
            except (TypeError, ValueError):
                self._heating = 0
            attributes = ["heating"]
            if self.heating_active != was_heating_active:
                attributes.append("heating_active")
            return attributes
        return super()._refresh_state_from_datapoint(datapoint)
