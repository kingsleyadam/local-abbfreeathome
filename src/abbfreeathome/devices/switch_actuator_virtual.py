"""Free@Home SwitchActuatorVirtual Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class SwitchActuatorVirtual(Base):
    """Free@Home SwitchActuatorVirtual Class."""

    _state_refresh_input_pairings: list[Pairing] = [
        Pairing.AL_SWITCH_ON_OFF,
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
        """Initialize the Free@Home SwitchActuatorVirtual class."""
        self._state: bool | None = None

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

    async def turn_on(self):
        """Turn on the switch."""
        await self._set_switching_datapoint("1")
        self._state = True

    async def turn_off(self):
        """Turn on the switch."""
        await self._set_switching_datapoint("0")
        self._state = False

    def _refresh_state_from_input(self, input: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given input.

        This will return whether the state was refreshed as a boolean value.
        """
        if input.get("pairingID") == Pairing.AL_SWITCH_ON_OFF.value:
            self._state = input.get("value") == "1"
            return True
        return False

    async def _set_switching_datapoint(self, value: str):
        """Set the switching datapoint on the api."""
        _output_id, _output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_INFO_ON_OFF
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_output_id,
            value=value,
        )