"""Free@Home Base Class."""

from collections.abc import Callable
from typing import Any

from ..api import FreeAtHomeApi
from ..exceptions import InvalidDeviceChannelPairingId


class Base:
    """Free@Home Base Class."""

    _callbacks = set()

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
        """Initialize the Free@Home Base class."""
        self._device_id = device_id
        self._device_name = device_name
        self._channel_id = channel_id
        self._channel_name = channel_name
        self._api = api
        self._inputs = inputs
        self._outputs = outputs
        self._parameters = parameters
        self._floor_name = floor_name
        self._room_name = room_name

    @property
    def device_id(self) -> str:
        """Get the device id."""
        return self._device_id

    @property
    def device_name(self) -> str:
        """Get the device name."""
        return self._device_name

    @property
    def channel_id(self) -> str:
        """Get the channel id."""
        return self._channel_id

    @property
    def channel_name(self) -> str:
        """Get the name of the channel."""
        return self._channel_name

    @property
    def floor_name(self) -> str | None:
        """Get the floor name of the device."""
        return self._floor_name

    @property
    def room_name(self) -> str | None:
        """Get the room name of the device."""
        return self._room_name

    def get_input_by_pairing_id(self, pairing_id: int) -> tuple[str, Any]:
        """Get the channel input by pairing id."""
        for _input_id, _input in self._inputs.items():
            if _input.get("pairingID") == pairing_id:
                return _input_id, _input.get("value")

        raise InvalidDeviceChannelPairingId(self.device_id, self.channel_id, pairing_id)

    def get_output_by_pairing_id(self, pairing_id: int) -> tuple[str, Any]:
        """Get the channel output by pairing id."""
        for _output_id, _output in self._outputs.items():
            if _output.get("pairingID") == pairing_id:
                return _output_id, _output.get("value")

        raise InvalidDeviceChannelPairingId(self.device_id, self.channel_id, pairing_id)

    def update_device():
        """Update a devices state."""

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when switch changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)
