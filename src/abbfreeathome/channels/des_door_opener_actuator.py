"""Free@Home DesDoorOpenerActuator Class."""

from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class DesDoorOpenerActuator(Base):
    """Free@Home DesDoorOpenerActuator Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_INFO_ON_OFF,
    ]
    _callback_attributes: list[str] = [
        "state",
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
        """Initialize the Free@Home DesDoorOpenerActuator class."""
        self._state: bool | None = None

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
        """Get the state of the DesDoorOpenerActuator."""
        return self._state

    async def lock(self):
        """Lock the door."""
        await self._set_switching_datapoint("0")
        self._state = False

    async def unlock(self):
        """Unlock the door."""
        await self._set_switching_datapoint("1")
        self._state = True

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        if datapoint.get("pairingID") == Pairing.AL_INFO_ON_OFF.value:
            self._state = datapoint.get("value") == "1"
            return "state"
        return None

    async def _set_switching_datapoint(self, value: str):
        """Set the switching datapoint on the api."""
        _switch_input_id, _switch_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_TIMED_START_STOP
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_switch_input_id,
            value=value,
        )
