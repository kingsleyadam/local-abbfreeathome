"""Free@Home SwitchActuator Class."""

import logging
from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing_id import PairingId
from .base import Base

_LOGGER = logging.getLogger(__name__)


class SwitchActuator(Base):
    """Free@Home SwitchActuator Class."""

    _state = None

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
        """Initialize the Free@Home SwitchActuator class."""
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

        # Set the initial state of the switch based on output
        self._refresh_state_from_outputs()

    @property
    def state(self):
        """Get the state of the switch."""
        return self._state

    async def turn_on(self):
        """Turn on the switch."""
        await self._set_switching_datapoint("1")
        self._state = True

    async def turn_off(self):
        """Turn on the switch."""
        await self._set_switching_datapoint("0")
        self._state = False

    async def refresh_state(self):
        """Refresh the state of the switch from the api."""
        _switch_output_id, _switch_output_value = self.get_output_by_pairing_id(
            pairing_id=PairingId.AL_INFO_ON_OFF.value
        )

        _datapoint = (
            await self._api.get_datapoint(
                device_id=self.device_id,
                channel_id=self.channel_id,
                datapoint=_switch_output_id,
            )
        )[0]

        self._state = _datapoint == "1"

    def _refresh_state_from_inputs(self):
        """Refresh the state of the switch from the _inputs."""

    def _refresh_state_from_outputs(self):
        """Refresh the state of the switch from the _outputs."""
        _switch_output_id, _switch_output_value = self.get_output_by_pairing_id(
            pairing_id=PairingId.AL_INFO_ON_OFF.value
        )
        self._state = _switch_output_value == "1"

    async def _set_switching_datapoint(self, value: str):
        _switch_input_id, _switch_input_value = self.get_input_by_pairing_id(
            pairing_id=PairingId.AL_SWITCH_ON_OFF.value
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_switch_input_id,
            value=value,
        )

    def update_device(self, datapoint_key: str, datapoint_value: str):
        """Update the switch state."""
        _LOGGER.info(
            "%s received updated data: %s: %s",
            self.channel_name,
            datapoint_key,
            datapoint_value,
        )
        _io_key = datapoint_key.split("/")[-1]
        if _io_key in self._inputs:
            self._inputs[_io_key]["value"] = datapoint_value
            self._refresh_state_from_inputs()
        if _io_key in self._outputs:
            self._outputs[_io_key]["value"] = datapoint_value
            self._refresh_state_from_outputs()

        for callback in self._callbacks:
            callback()
