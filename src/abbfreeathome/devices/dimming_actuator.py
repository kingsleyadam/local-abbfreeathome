"""Free@Home DimmingActuator Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class DimmingActuator(Base):
    """Free@Home DimmingActuator Class."""

    _state = None
    _brightness = None

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
    def state(self) -> bool:
        """Get the state of the dimming actuator."""
        return bool(self._state)

    @property
    def brightness(self) -> int:
        """Get the brightness level of the dimmer."""
        return int(self._brightness)

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

    async def refresh_state(self):
        """Refresh the state of the device from the api."""
        _state_refresh_pairings = [
            Pairing.AL_INFO_ON_OFF,
            Pairing.AL_INFO_ACTUAL_DIMMING_VALUE,
        ]

        for _pairing in _state_refresh_pairings:
            _switch_output_id, _switch_output_value = self.get_output_by_pairing(
                pairing=_pairing
            )

            _datapoint = (
                await self._api.get_datapoint(
                    device_id=self.device_id,
                    channel_id=self.channel_id,
                    datapoint=_switch_output_id,
                )
            )[0]

            self._refresh_state_from_output(
                output={
                    "pairingID": _pairing.value,
                    "value": _datapoint,
                }
            )

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
