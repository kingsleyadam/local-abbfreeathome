"""Free@Home HeatingActuator Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class HeatingActuator(Base):
    """Free@Home HeatingActuator Class."""

    _state_refresh_output_pairings: list[Pairing] = [
        Pairing.AL_INFO_VALUE_HEATING,
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
        """Initialize the Free@Home HeatingActuator class."""
        self._state: int | None = None

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
        """Get the state of the actuator."""
        return self._state

    async def set_state(self, value: int):
        """
        Set the open level of the heating valve.

        The position has to be between 0 and 100
        Fully closed = 0
        Fully open = 100
        Just as an information: This is exaclty the other way round as done in HA,
        so in HA we have to remember to convert the value with something like:
        abs(value-100)
        before sending it to this function
        """
        value = max(0, value)
        value = min(value, 100)

        await self._set_state_datapoint(str(value))
        self._state = value

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_INFO_VALUE_HEATING.value:
            self._state = int(output.get("value"))
            return True
        return False

    async def _set_state_datapoint(self, value: str):
        """Set the open level datapoint on the api."""
        _position_input_id, _position_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_ACTUATING_VALUE_HEATING
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_position_input_id,
            value=value,
        )
