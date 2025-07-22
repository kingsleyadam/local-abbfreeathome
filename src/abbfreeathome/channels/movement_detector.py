"""Free@Home MovementDetector and BlockableMovementDetector Class."""

from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from .base import Base

if TYPE_CHECKING:
    from ..device import Device


class MovementDetector(Base):
    """Free@Home MovementDetector Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_TIMED_MOVEMENT,
        Pairing.AL_BRIGHTNESS_LEVEL,
    ]
    _callback_attributes: list[str] = [
        "state",
        "brightness",
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
        """Initialize the Free@Home MovementDetector class."""
        self._state: bool | None = None
        self._brightness: float | None = None

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
        """Get the movement state."""
        return self._state

    @property
    def brightness(self) -> float | None:
        """Get the brightness level of the sensor."""
        return self._brightness

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """
        Refresh the state of the channel from a given output.

        This will return the name of the attribute, which was refreshed or None.
        """
        match datapoint.get("pairingID"):
            case Pairing.AL_TIMED_MOVEMENT.value:
                self._state = datapoint.get("value") == "1"
                return "state"
            case Pairing.AL_BRIGHTNESS_LEVEL.value:
                self._brightness = float(datapoint.get("value"))
                return "brightness"
            case _:
                return None


class BlockableMovementDetector(MovementDetector):
    """Free@Home BlockableMovementDetector Class."""

    _state_refresh_pairings: list[Pairing] = [
        Pairing.AL_TIMED_MOVEMENT,
        Pairing.AL_BRIGHTNESS_LEVEL,
        Pairing.AL_INFO_LOCKED_SENSOR,
    ]
    _callback_attributes: list[str] = [
        "state",
        "brightness",
        "blocked",
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
        """Initialize the Free@Home BlockableMovementDetector class."""
        self._blocked: bool | None = None

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
    def blocked(self) -> bool | None:
        """Get the blocked state of the sensor."""
        return self._blocked

    async def turn_on_blocked(self):
        """Block the sensor."""
        await self._set_blocking_datapoint("1")
        self._blocked = True

    async def turn_off_blocked(self):
        """Unblock the sensor."""
        await self._set_blocking_datapoint("0")
        self._blocked = False

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        if datapoint.get("pairingID") == Pairing.AL_INFO_LOCKED_SENSOR.value:
            self._blocked = datapoint.get("value") == "1"
            return "blocked"
        return super()._refresh_state_from_datapoint(datapoint)

    async def _set_blocking_datapoint(self, value: str):
        """Set the blocking datapoint on the api."""
        _blocking_input_id, _ = self.get_input_by_pairing(
            pairing=Pairing.AL_LOCK_SENSOR
        )
        return await self.device.api.set_datapoint(
            device_serial=self.device_serial,
            channel_id=self.channel_id,
            datapoint=_blocking_input_id,
            value=value,
        )
