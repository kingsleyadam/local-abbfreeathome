"""Free@Home Base Class."""

from collections.abc import Callable
import logging
from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from ..exceptions import InvalidDeviceChannelPairing

_LOGGER = logging.getLogger(__name__)


class Base:
    """Free@Home Base Class."""

    _state_refresh_output_pairings: list[Pairing] = []

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
        self._callbacks = set()

        # Set the initial state of the device based on output
        self._refresh_state_from_outputs()

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

    def get_input_by_pairing(self, pairing: Pairing) -> tuple[str, Any]:
        """Get the channel input by pairing id."""
        for _input_id, _input in self._inputs.items():
            if _input.get("pairingID") == pairing.value:
                return _input_id, _input.get("value")

        raise InvalidDeviceChannelPairing(
            self.device_id, self.channel_id, pairing.value
        )

    def get_output_by_pairing(self, pairing: Pairing) -> tuple[str, Any]:
        """Get the channel output by pairing id."""
        for _output_id, _output in self._outputs.items():
            if _output.get("pairingID") == pairing.value:
                return _output_id, _output.get("value")

        raise InvalidDeviceChannelPairing(
            self.device_id, self.channel_id, pairing.value
        )

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
            _refreshed = self._refresh_state_from_output(output=self._outputs[_io_key])

        if _refreshed and self._callbacks:
            for callback in self._callbacks:
                callback()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when device changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    async def refresh_state(self):
        """Refresh the state of the device from the api."""
        for _pairing in self._state_refresh_output_pairings:
            _output_id, _output_value = self.get_output_by_pairing(pairing=_pairing)

            _datapoint = (
                await self._api.get_datapoint(
                    device_id=self.device_id,
                    channel_id=self.channel_id,
                    datapoint=_output_id,
                )
            )[0]

            self._refresh_state_from_output(
                output={
                    "pairingID": _pairing.value,
                    "value": _datapoint,
                }
            )

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """Refresh the state of the device from a single output."""

    def _refresh_state_from_outputs(self):
        """Refresh the state of the device from the _outputs."""
        for _output in self._outputs.values():
            self._refresh_state_from_output(_output)
