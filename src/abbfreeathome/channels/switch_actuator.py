"""Free@Home SwitchActuator Class."""

import enum
from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class SwitchActuatorForcedPosition(enum.Enum):
    """An Enum class for the force states."""

    unknown = None
    deactivated = "0"
    forced_on = "4"
    forced_off = "5"


class SwitchActuator(Base):
    """Free@Home SwitchActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_FORCE,
        Pairing.AL_INFO_ON_OFF,
    ]
    _callback_attributes: list[str] = [
        "state",
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
        """Initialize the Free@Home SwitchActuator class."""
        self._state: bool | None = None
        self._forced_position: SwitchActuatorForcedPosition = (
            SwitchActuatorForcedPosition.unknown
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

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if datapoint.get("pairingID") == Pairing.AL_INFO_ON_OFF.value:
            self._state = datapoint.get("value") == "1"
            return "state"
        if datapoint.get("pairingID") == Pairing.AL_INFO_FORCE.value:
            try:
                self._forced_position = SwitchActuatorForcedPosition(
                    datapoint.get("value")
                )
            except ValueError:
                self._forced_position = SwitchActuatorForcedPosition.unknown
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

    async def _set_force_datapoint(self, value: str):
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
