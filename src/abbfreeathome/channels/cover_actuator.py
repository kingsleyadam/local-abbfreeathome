"""Free@Home abstract CoverActuator Class."""

import enum
from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class CoverActuatorForcedPosition(enum.Enum):
    """An Enum class for the force_position states."""

    unknown = None
    deactivated = "0"
    forced_open = "2"
    forced_closed = "3"


class CoverActuatorState(enum.Enum):
    """An Enum class for the cover states."""

    unknown = None
    opened = "0"
    partly_opened = "1"
    opening = "2"
    closing = "3"


class CoverActuator(Base):
    """Free@Home CoverActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_MOVE_UP_DOWN,
        Pairing.AL_CURRENT_ABSOLUTE_POSITION_BLINDS_PERCENTAGE,
        Pairing.AL_INFO_FORCE,
    ]
    _callback_attributes: list[str] = [
        "state",
        "forced_position",
        "position",
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
        """Initialize the Free@Home CoverActuator class."""
        self._state: CoverActuatorState = CoverActuatorState.unknown
        self._position: int | None = None
        self._forced_position: CoverActuatorForcedPosition = (
            CoverActuatorForcedPosition.unknown
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
    def state(self) -> str:
        """Get the state of the cover actuator."""
        return self._state.name

    @property
    def position(self) -> int | None:
        """Get the position of the cover."""
        return self._position

    @property
    def forced_position(self) -> str | None:
        """Get the information, if the position is forced."""
        return self._forced_position.name

    async def open(self):
        """Open the cover."""
        await self._set_moving_datapoint("0")

    async def close(self):
        """Close the cover."""
        await self._set_moving_datapoint("1")

    async def stop(self):
        """Stop the movement of the cover."""
        if self.state in [
            CoverActuatorState.opening.name,
            CoverActuatorState.closing.name,
        ]:
            await self._set_stop_datapoint()

    async def set_forced_position(self, forced_position_name: str):
        """Force the position of the cover."""
        try:
            _position = CoverActuatorForcedPosition[forced_position_name]
        except KeyError:
            _position = CoverActuatorForcedPosition.unknown

        await self._set_force_datapoint(_position.value)
        self._forced_position = _position

    async def set_position(self, value: int):
        """
        Set the position of the cover.

        The position has to be between 0 and 100
        Fully open = 0
        Fully closed = 100
        Just as an information: This is exaclty the other way round as done in HA,
        so in HA we have to remember to convert the value with something like:
        abs(value-100)
        before sending it to this function
        """
        value = max(0, value)
        value = min(value, 100)

        await self._set_position_datapoint(str(value))
        self._position = value

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if datapoint.get("pairingID") == Pairing.AL_INFO_MOVE_UP_DOWN.value:
            try:
                self._state = CoverActuatorState(datapoint.get("value"))
            except ValueError:
                self._state = CoverActuatorState.unknown
            return "state"
        if datapoint.get("pairingID") == Pairing.AL_INFO_FORCE.value:
            try:
                self._forced_position = CoverActuatorForcedPosition(
                    datapoint.get("value")
                )
            except ValueError:
                self._forced_position = CoverActuatorForcedPosition.unknown
            return "forced_position"
        if (
            datapoint.get("pairingID")
            == Pairing.AL_CURRENT_ABSOLUTE_POSITION_BLINDS_PERCENTAGE.value
        ):
            self._position = int(float(datapoint.get("value")))
            return "position"
        return None

    async def _set_moving_datapoint(self, value: str):
        """Set the move_up_down datapoint on the api."""
        _move_input_id, _move_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_MOVE_UP_DOWN
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_move_input_id,
            value=value,
        )

    async def _set_position_datapoint(self, value: str):
        """Set the position datapoint on the api."""
        _position_input_id, _position_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_SET_ABSOLUTE_POSITION_BLINDS_PERCENTAGE
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_position_input_id,
            value=value,
        )

    async def _set_force_datapoint(self, value: str):
        """Set the force datapoint on the api."""
        _force_input_id, _force_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_FORCED_UP_DOWN
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_force_input_id,
            value=value,
        )

    async def _set_stop_datapoint(self):
        """Set the position datapoint on the api."""
        _stop_input_id, _stop_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_STOP_STEP_UP_DOWN
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_stop_input_id,
            value="1",
        )


class AtticWindowActuator(CoverActuator):
    """Free@Home AtticWindowActuator Class."""


class AwningActuator(CoverActuator):
    """Free@Home AwningActuator Class."""


class BlindActuator(CoverActuator):
    """Free@Home BlindActuator Class."""


class ShutterActuator(CoverActuator):
    """Free@Home ShutterActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_MOVE_UP_DOWN,
        Pairing.AL_CURRENT_ABSOLUTE_POSITION_BLINDS_PERCENTAGE,
        Pairing.AL_INFO_FORCE,
        Pairing.AL_CURRENT_ABSOLUTE_POSITION_SLATS_PERCENTAGE,
    ]
    _callback_attributes: list[str] = [
        "state",
        "forced_position",
        "position",
        "tilt_position",
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
        """Initialize the Free@Home ShutterActuator class."""
        self._tilt_position: int | None = None

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
    def tilt_position(self) -> int | None:
        """Get the tilt position of the cover."""
        return self._tilt_position

    async def set_tilt_position(self, value: int):
        """
        Set the tilt position of the cover.

        The tilt position has to be between 0 and 100
        Fully open = 0
        Fully closed = 100
        Just as an information: This is exaclty the other way round as done in HA,
        so in HA we have to remember to convert the value with something like:
        abs(value-100)
        before sending it to this function
        """
        value = max(0, value)
        value = min(value, 100)

        await self._set_tilt_datapoint(str(value))
        self._tilt_position = value

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if (
            datapoint.get("pairingID")
            == Pairing.AL_CURRENT_ABSOLUTE_POSITION_SLATS_PERCENTAGE.value
        ):
            self._tilt_position = int(float(datapoint.get("value")))
            return "tilt_position"
        return super()._refresh_state_from_datapoint(datapoint)

    async def _set_tilt_datapoint(self, value: str):
        """Set the tilt position datapoint on the api."""
        _tilt_input_id, _tilt_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_SET_ABSOLUTE_POSITION_SLATS_PERCENTAGE
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_tilt_input_id,
            value=value,
        )
