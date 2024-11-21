"""Free@Home SwitchActuator Class."""

import enum
from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class SwitchActuatorForcedPosition(enum.Enum):
    """An Enum class for the force states."""

    unknown = None
    deactivated = "0"
    forced_on = "4"
    forced_off = "5"


class SwitchActuator(Base):
    """Free@Home SwitchActuator Class."""

    _state_refresh_output_pairings: list[Pairing] = [
        Pairing.AL_INFO_FORCE,
        Pairing.AL_INFO_ON_OFF,
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
        virtual_device: bool = False,
    ) -> None:
        """Initialize the Free@Home SwitchActuator class."""
        self._state: bool | None = None
        self._forced_position: SwitchActuatorForcedPosition = (
            SwitchActuatorForcedPosition.unknown
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
            virtual_device,
        )

    @property
    def state(self) -> bool | None:
        """Get the state of the switch."""
        return self._state

    @property
    def forced_position(self) -> str | None:
        """Get the forced state of the switch."""
        return self._forced_position.name

    async def turn_on(self):
        """Turn on the switch."""
        await self._set_switching_datapoint("1")
        self._state = True

    async def turn_off(self):
        """Turn on the switch."""
        await self._set_switching_datapoint("0")
        self._state = False

    async def set_forced_position(self, forced_position_name: str):
        """Set the forced-option on the switch."""
        try:
            _position = SwitchActuatorForcedPosition[forced_position_name]
        except KeyError:
            _position = SwitchActuatorForcedPosition.unknown

        if _position == SwitchActuatorForcedPosition.deactivated:
            await self._set_force_datapoint("0")
        if _position == SwitchActuatorForcedPosition.forced_on:
            await self._set_force_datapoint("3")
        if _position == SwitchActuatorForcedPosition.forced_off:
            await self._set_force_datapoint("2")

        self._forced_position = _position

    async def _vd_acknowledgement(
        self, datapoint_key: str, datapoint_value: str
    ) -> bool:
        _io_key = datapoint_key.split("/")[-1]

        try:
            _input = self._inputs[_io_key]
        except KeyError:
            return False

        if _input.get("pairingID") == Pairing.AL_SWITCH_ON_OFF.value:
            _switch_datapoint_id, _switch_datapoint_value = self.get_output_by_pairing(
                pairing=Pairing.AL_INFO_ON_OFF
            )
            return await self._api.set_datapoint(
                device_id=self.device_id,
                channel_id=self.channel_id,
                datapoint=_switch_datapoint_id,
                value=datapoint_value,
            )
        return False

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_INFO_ON_OFF.value:
            self._state = output.get("value") == "1"
            return True
        if output.get("pairingID") == Pairing.AL_INFO_FORCE.value:
            try:
                self._forced_position = SwitchActuatorForcedPosition(
                    output.get("value")
                )
            except ValueError:
                self._forced_position = SwitchActuatorForcedPosition.unknown
            return True
        return False

    async def _set_switching_datapoint(self, value: str):
        """Set the switching datapoint on the api."""
        if self.virtual_device:
            _switch_datapoint_id, _switch_datapoint_value = self.get_output_by_pairing(
                pairing=Pairing.AL_INFO_ON_OFF
            )
        else:
            _switch_datapoint_id, _switch_datapoint_value = self.get_input_by_pairing(
                pairing=Pairing.AL_SWITCH_ON_OFF
            )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_switch_datapoint_id,
            value=value,
        )

    async def _set_force_datapoint(self, value: str):
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
