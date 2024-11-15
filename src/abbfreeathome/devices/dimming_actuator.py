"""Free@Home DimmingActuator Class."""

import enum
from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class DimmingActuatorForcedPosition(enum.Enum):
    """An Enum class for the force states."""

    unknown = None
    deactivated = "0"
    forced_on = "4"
    forced_off = "5"


class DimmingActuator(Base):
    """Free@Home DimmingActuator Class."""

    _state_refresh_output_pairings: list[Pairing] = [
        Pairing.AL_INFO_FORCE,
        Pairing.AL_INFO_ON_OFF,
        Pairing.AL_INFO_ACTUAL_DIMMING_VALUE,
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
        """Initialize the Free@Home DimmingActuator class."""
        self._state: bool | None = None
        self._brightness: int | None = None
        self._forced_position: DimmingActuatorForcedPosition = (
            DimmingActuatorForcedPosition.unknown
        )

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

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_INFO_ON_OFF.value:
            self._state = output.get("value") == "1"
            return True
        if output.get("pairingID") == Pairing.AL_INFO_ACTUAL_DIMMING_VALUE.value:
            self._brightness = output.get("value")
            return True
        if output.get("pairingID") == Pairing.AL_INFO_FORCE.value:
            try:
                self._forced_position = DimmingActuatorForcedPosition(
                    output.get("value")
                )
            except ValueError:
                self._forced_position = DimmingActuatorForcedPosition.unknown
            return True
        return False

    async def _set_switching_datapoint(self, value: str):
        """Set the switching datapoint on the api."""
        _switch_input_id, _switch_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_SWITCH_ON_OFF
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_switch_input_id,
            value=value,
        )

    async def _set_brightness_datapoint(self, value: str):
        """Set the brightness datapoint on the api."""
        _brightness_input_id, _brightness_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_ABSOLUTE_SET_VALUE_CONTROL
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_brightness_input_id,
            value=value,
        )

    async def _set_forced_datapoint(self, value: str):
        """Set the force datapoint on the api."""
        _force_input_id, _force_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_FORCED
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_force_input_id,
            value=value,
        )
