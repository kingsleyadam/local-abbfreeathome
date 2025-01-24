"""Free@Home Virtual SwitchActuator class."""

import enum
from typing import Any

from ...api import FreeAtHomeApi
from ...bin.pairing import Pairing
from .virtual_base import VirtualBase


class VirtualSwitchActuatorForcedPosition(enum.Enum):
    """An Enum class for the force states."""

    unknown = None
    deactivated = "0"
    forced_on = "3"
    forced_off = "2"


class VirtualSwitchActuator(VirtualBase):
    """Free@Home Virtual SwitchActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_SWITCH_ON_OFF,
        Pairing.AL_FORCED,
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
    ):
        """Initialize the Free@Home Virtual SwitchActuator class."""
        self._state: bool | None = None
        self._forced_position: VirtualSwitchActuatorForcedPosition = (
            VirtualSwitchActuatorForcedPosition.unknown
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
    def state(self) -> bool | None:
        """Get the state of the switch."""
        return self._state

    @property
    def forced_position(self) -> str | None:
        """Get the forced state of the switch."""
        return self._forced_position.name

    async def set_on(self):
        """Turn on the switch."""
        await self._set_switching_datapoint("1")
        self._state = True

    async def set_off(self):
        """Turn off the switch."""
        await self._set_switching_datapoint("0")
        self._state = False

    async def set_forced_position(self, forced_position_name: str):
        """Set the forced-option on the switch."""
        try:
            _position = VirtualSwitchActuatorForcedPosition[forced_position_name]
        except KeyError:
            _position = VirtualSwitchActuatorForcedPosition.unknown

        if _position == VirtualSwitchActuatorForcedPosition.deactivated:
            await self._set_force_datapoint("0")
        elif _position == VirtualSwitchActuatorForcedPosition.forced_on:
            await self._set_force_datapoint("4")
        elif _position == VirtualSwitchActuatorForcedPosition.forced_off:
            await self._set_force_datapoint("5")

        self._forced_position = _position

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given input.

        This will return whether the state was refreshed as a boolean value.
        """
        if datapoint.get("pairingID") == Pairing.AL_SWITCH_ON_OFF.value:
            self._state = datapoint.get("value") == "1"
            return True
        if datapoint.get("pairingID") == Pairing.AL_FORCED.value:
            try:
                self._forced_position = VirtualSwitchActuatorForcedPosition(
                    datapoint.get("value")
                )
            except ValueError:
                self._forced_position = VirtualSwitchActuatorForcedPosition.unknown
            return True
        return False

    async def _set_switching_datapoint(self, value: str):
        """Set the switching datapoint on the api."""
        _switch_output_id, _switch_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_INFO_ON_OFF
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_switch_output_id,
            value=value,
        )

    async def _set_force_datapoint(self, value: str):
        """Set the force datapoint on the api."""
        _force_output_id, _force_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_INFO_FORCE
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_force_output_id,
            value=value,
        )
