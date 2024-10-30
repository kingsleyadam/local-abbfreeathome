"""Free@Home BlindActuator Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class BlindActuator(Base):
    """Free@Home BlindActuator Class."""

    _state_refresh_output_pairings: list[Pairing] = [
        Pairing.AL_INFO_MOVE_UP_DOWN,
        Pairing.AL_CURRENT_ABSOLUTE_POSITION_BLINDS_PERCENTAGE,
        Pairing.AL_INFO_FORCE,
        Pairing.AL_CURRENT_ABSOLUTE_POSITION_SLATS_PERCENTAGE,
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
        """Initialize the Free@Home BlindActuator class."""
        self._state: int | None = None
        self._position: int | None = None
        self._forced_position: int | None = None
        self._tilt_position: int | None = None

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
    def state(self) -> int | None:
        """Get the state of the blind actuator."""
        return int(self._state)

    @property
    def position(self) -> int:
        """Get the position of the blind."""
        return int(self._position)

    @property
    def forced_position(self) -> int:
        """Get the information, if the position is forced."""
        return int(self._forced_position)

    @property
    def tilt_position(self) -> int:
        """Get the tilt position of the blind."""
        return int(self._tilt_position)

    def is_cover_closed(self):
        """Helper-Function returns true if the cover is closed."""
        return self.position == 0

    def is_cover_opening(self):
        """Helper-Function returns true if the cover is opening."""
        return self.state == 2

    def is_cover_closing(self):
        """Helper-Function returns true if the cover is closing."""
        return self.state == 3

    def supports_tilt_position(self):
        """Return true if cover supports tilt position."""
        for _value in self._inputs.values():
            if (
                _value["pairingID"]
                == Pairing.AL_SET_ABSOLUTE_POSITION_SLATS_PERCENTAGE.value
            ):
                return True

        return False

    async def open(self):
        """Open the blind."""
        await self._set_moving_datapoint("0")

    async def close(self):
        """Close the blind."""
        await self._set_moving_datapoint("1")

    async def stop(self):
        """Stop the movement of the blind."""
        if self.state in [2, 3]:
            await self._set_stop_datapoint()

    async def force_position(self, value: int):
        """
        Force the position of the blind.

        0 means none
        2 means open
        3 means close
        """
        if value in [0, 2, 3]:
            await self._set_force_datapoint(str(value))

    async def set_position(self, value: int):
        """
        Set the position of the blind.

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

    async def set_tilt_position(self, value: int):
        """
        Set the tilt position of the blind.

        The tilt position has to be between 0 and 100
        Fully open = 0
        Fully closed = 100
        Just as an information: This is exaclty the other way round as done in HA,
        so in HA we have to remember to convert the value with something like:
        abs(value-100)
        before sending it to this function
        """
        if self.supports_tilt_position():
            value = max(0, value)
            value = min(value, 100)

            await self._set_tilt_datapoint(str(value))
            self._tilt_position = value

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_INFO_MOVE_UP_DOWN.value:
            """
            0 means the blind is fully opened
            1 means the blind is partly opened
            2 means the blind is currently opening
            3 means the blind is currently closing
            """
            try:
                self._state = output.get("value")
            except ValueError:
                self._state = -1
            return True
        if output.get("pairingID") == Pairing.AL_INFO_FORCE.value:
            """
            0 means none
            2 means open
            3 means close
            """
            try:
                self._forced_position = output.get("value")
            except ValueError:
                self._forced_position = -1
            return True
        if (
            output.get("pairingID")
            == Pairing.AL_CURRENT_ABSOLUTE_POSITION_BLINDS_PERCENTAGE.value
        ):
            self._position = output.get("value")
            return True
        if (
            output.get("pairingID")
            == Pairing.AL_CURRENT_ABSOLUTE_POSITION_SLATS_PERCENTAGE.value
        ):
            self._tilt_position = output.get("value")
            return True
        return False

    async def _set_moving_datapoint(self, value: str):
        """Set the move_up_down datapoint on the api."""
        _move_input_id, _move_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_MOVE_UP_DOWN
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_move_input_id,
            value=value,
        )

    async def _set_position_datapoint(self, value: str):
        """Set the position datapoint on the api."""
        _position_input_id, _position_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_SET_ABSOLUTE_POSITION_BLINDS_PERCENTAGE
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_position_input_id,
            value=value,
        )

    async def _set_tilt_datapoint(self, value: str):
        """Set the tilt position datapoint on the api."""
        _tilt_input_id, _tilt_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_SET_ABSOLUTE_POSITION_SLATS_PERCENTAGE
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_tilt_input_id,
            value=value,
        )

    async def _set_force_datapoint(self, value: str):
        """Set the force datapoint on the api."""
        _force_input_id, _force_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_FORCED_UP_DOWN
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_force_input_id,
            value=value,
        )

    async def _set_stop_datapoint(self):
        """Set the position datapoint on the api."""
        _stop_input_id, _stop_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_STOP_STEP_UP_DOWN
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_stop_input_id,
            value="1",
        )
