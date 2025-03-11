"""Free@Home Virtual SwitchActuator class."""

# import enum
import logging
from typing import Any

from ...api import FreeAtHomeApi
from ...bin.pairing import Pairing
from ..base import Base

_LOGGER = logging.getLogger(__name__)


# class VirtualSwitchActuatorForcedPosition(enum.Enum):
#    """An Enum class for the force states."""

#    unknown = None
#    deactivated = "0"
#    forced_on = "3"
#    forced_off = "2"


class VirtualSwitchActuator(Base):
    """Free@Home Virtual SwitchActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_ON_OFF,
        #        Pairing.AL_INFO_FORCE,
    ]

    _input_refresh_pairings: list[Pairing] = [
        Pairing.AL_SWITCH_ON_OFF,
        #        Pairing.AL_FORCED,
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
        #        self._forced_position: VirtualSwitchActuatorForcedPosition = (
        #            VirtualSwitchActuatorForcedPosition.unknown
        #        )
        self._requested_state: bool | None = None
        # self._requested_forced_position: VirtualSwitchActuatorForcedPosition = (
        #     VirtualSwitchActuatorForcedPosition.unknown
        # )

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
    def requested_state(self) -> bool | None:
        """Get the requested state of the switch."""
        return self._requested_state

    #    @property
    #    def forced_position(self) -> str | None:
    #        """Get the forced state of the switch."""
    #        return self._forced_position.name

    #    @property
    #    def requested_forced_position(self) -> str | None:
    #        """Get the requested forced state of the switch."""
    #        return self._requested_forced_position.name

    async def turn_on(self):
        """Turn on the switch."""
        await self._set_switching_datapoint("1")
        self._state = True

    async def turn_off(self):
        """Turn off the switch."""
        await self._set_switching_datapoint("0")
        self._state = False

    #    async def set_forced_position(self, forced_position_name: str):
    #        """Set the forced-option on the switch."""
    #        try:
    #            _position = VirtualSwitchActuatorForcedPosition[forced_position_name]
    #        except KeyError:
    #            _position = VirtualSwitchActuatorForcedPosition.unknown
    #
    #        if _position == VirtualSwitchActuatorForcedPosition.deactivated:
    #            await self._set_force_datapoint("0")
    #        elif _position == VirtualSwitchActuatorForcedPosition.forced_on:
    #            await self._set_force_datapoint("4")
    #        elif _position == VirtualSwitchActuatorForcedPosition.forced_off:
    #            await self._set_force_datapoint("5")
    #
    #        self._forced_position = _position

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given input and output.

        This will return whether the state was refreshed as a boolean value.
        """
        if datapoint.get("pairingID") == Pairing.AL_SWITCH_ON_OFF.value:
            self._requested_state = datapoint.get("value") == "1"
            return True
        # if datapoint.get("pairingID") == Pairing.AL_FORCED.value:
        #     try:
        #         self._requested_forced_position = VirtualSwitchActuatorForcedPosition(
        #             datapoint.get("value")
        #         )
        #     except ValueError:
        #         self._requested_forced_position = (
        #             VirtualSwitchActuatorForcedPosition.unknown
        #         )
        #     return True
        if datapoint.get("pairingID") == Pairing.AL_INFO_ON_OFF.value:
            self._state = datapoint.get("value") == "1"
            return True
        # if datapoint.get("pairingID") == Pairing.AL_INFO_FORCE.value:
        #     try:
        #         self._forced_position = VirtualSwitchActuatorForcedPosition(
        #             datapoint.get("value")
        #         )
        #     except ValueError:
        #         self._forced_position = VirtualSwitchActuatorForcedPosition.unknown
        #     return True
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

    #    async def _set_force_datapoint(self, value: str):
    #        """Set the force datapoint on the api."""
    #        _force_output_id, _force_output_value = self.get_output_by_pairing(
    #            pairing=Pairing.AL_INFO_FORCE
    #        )
    #        return await self._api.set_datapoint(
    #            device_id=self.device_id,
    #            channel_id=self.channel_id,
    #            datapoint=_force_output_id,
    #            value=value,
    #        )

    def update_device(self, datapoint_key: str, datapoint_value: str):
        """Update the device state."""
        _LOGGER.info(
            "%s received updated data: %s: %s",
            self.channel_name,
            datapoint_key,
            datapoint_value,
        )
        _refreshed = None
        _io_key = datapoint_key.split("/")[-1]

        if _io_key in self._outputs:
            self._outputs[_io_key]["value"] = datapoint_value
            _refreshed = self._refresh_state_from_datapoint(
                datapoint=self._outputs[_io_key]
            )

        if _io_key in self._inputs:
            self._inputs[_io_key]["value"] = datapoint_value
            _refreshed = self._refresh_state_from_datapoint(
                datapoint=self._inputs[_io_key]
            )

        if _refreshed and self._callbacks:
            for callback in self._callbacks:
                callback()

    # async def refresh_state(self):
    #     """Refresh the state of the device from the api."""
    #     for _pairing in self._state_refresh_pairings:
    #         _datapoint_id, _datapoint_value = self.get_output_by_pairing(
    #             pairing=_pairing
    #         )

    #         _datapoint = (
    #             await self._api.get_datapoint(
    #                 device_id=self.device_id,
    #                 channel_id=self.channel_id,
    #                 datapoint=_datapoint_id,
    #             )
    #         )[0]

    #         self._refresh_state_from_datapoint(
    #             datapoint={
    #                 "pairingID": _pairing.value,
    #                 "value": _datapoint,
    #             }
    #         )

    #     for _pairing in self._input_refresh_pairings:
    #         _datapoint_id, _datapoint_value = self.get_input_by_pairing(
    #             pairing=_pairing
    #         )

    #         _datapoint = (
    #             await self._api.get_datapoint(
    #                 device_id=self.device_id,
    #                 channel_id=self.channel_id,
    #                 datapoint=_datapoint_id,
    #             )
    #         )[0]

    #         self._refresh_state_from_datapoint(
    #             datapoint={
    #                 "pairingID": _pairing.value,
    #                 "value": _datapoint,
    #             }
    #         )

    # def _refresh_state_from_datapoints(self):
    #     """Refresh the state of the device from the datapoints."""
    #     for _datapoint in self._outputs.values():
    #         self._refresh_state_from_datapoint(_datapoint)

    #     for _datapoint in self._inputs.values():
    #         self._refresh_state_from_datapoint(_datapoint)
