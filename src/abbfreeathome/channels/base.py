"""Free@Home Base Class."""

from collections.abc import Callable
import logging
from typing import TYPE_CHECKING, Any

from ..bin.pairing import Pairing
from ..bin.parameter import Parameter
from ..exceptions import (
    InvalidDeviceChannelPairing,
    InvalidDeviceChannelParameter,
    UnknownCallbackAttributeException,
)

if TYPE_CHECKING:
    from ..device import Device

_LOGGER = logging.getLogger(__name__)


class Base:
    """Free@Home Base Class."""

    _state_refresh_pairings: list[Pairing] = []
    _callback_attributes: list[str] = []

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
        """Initialize the Free@Home Base class."""
        self._device = device
        self._channel_id = channel_id
        self._channel_name = channel_name
        self._inputs = inputs
        self._outputs = outputs
        self._parameters = parameters
        self._floor_name = floor_name
        self._room_name = room_name
        self._callbacks = {}

        # Set the initial state of the channel
        self._refresh_state_from_datapoints()

    @property
    def device_serial(self) -> str:
        """Get the device serial."""
        return self._device.device_serial

    @property
    def device_name(self) -> str:
        """Get the device name."""
        return self._device.display_name

    @property
    def unresponsive(self) -> bool:
        """Get unresponsive status via device."""
        return self._device.unresponsive

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
        """Get the floor name."""
        return self._floor_name

    @property
    def room_name(self) -> str | None:
        """Get the room name."""
        return self._room_name

    @property
    def is_virtual(self) -> bool | None:
        """Get the virtual-status of the device."""
        return self.device.is_virtual

    @property
    def device(self) -> "Device":
        """Get the parent Device object."""
        return self._device

    def get_input_by_pairing(self, pairing: Pairing) -> tuple[str, Any]:
        """Get the channel input by pairing id."""
        for _input_id, _input in self._inputs.items():
            if _input.get("pairingID") == pairing.value:
                return _input_id, _input.get("value")

        raise InvalidDeviceChannelPairing(
            self.device_serial, self.channel_id, pairing.value
        )

    def get_output_by_pairing(self, pairing: Pairing) -> tuple[str, Any]:
        """Get the channel output by pairing id."""
        for _output_id, _output in self._outputs.items():
            if _output.get("pairingID") == pairing.value:
                return _output_id, _output.get("value")

        raise InvalidDeviceChannelPairing(
            self.device_serial, self.channel_id, pairing.value
        )

    def get_channel_parameter(self, parameter: Parameter) -> tuple[str, Any]:
        """Get the channel parameter value by its name."""
        for _parameter_id, _parameter_value in self._parameters.items():
            _parameter_id_int = int(_parameter_id.lstrip("par"), 16)
            if _parameter_id_int == parameter.value:
                return _parameter_id, _parameter_value

        raise InvalidDeviceChannelParameter(
            self.device_serial, self.channel_id, parameter.name
        )

    def update_channel(self, datapoint_key: str, datapoint_value: str):
        """Update the channel state."""
        _LOGGER.info(
            "%s received updated data: %s: %s",
            self.channel_name,
            datapoint_key,
            datapoint_value,
        )
        _callback_attribute = None
        _io_key = datapoint_key.split("/")[-1]

        if _io_key in self._outputs:
            self._outputs[_io_key]["value"] = datapoint_value
            _callback_attribute = self._refresh_state_from_datapoint(
                datapoint=self._outputs[_io_key]
            )

        if _callback_attribute and self._callbacks[_callback_attribute]:
            for callback in self._callbacks[_callback_attribute]:
                callback()

    def register_callback(
        self, callback_attribute: str, callback: Callable[[], None]
    ) -> None:
        """Register callback, called when channel changes state."""
        if callback_attribute in self._callback_attributes:
            if callback_attribute not in self._callbacks:
                self._callbacks[callback_attribute] = set()

            self._callbacks[callback_attribute].add(callback)
        else:
            raise UnknownCallbackAttributeException(
                unknown_attribute=callback_attribute,
                known_attributes=",".join(self._callback_attributes),
            )

    def remove_callback(
        self, callback_attribute: str, callback: Callable[[], None]
    ) -> None:
        """Remove previously registered callback."""
        if self._callbacks[callback_attribute]:
            self._callbacks[callback_attribute].discard(callback)

    async def refresh_state(self):
        """Refresh the state of the channel from the api."""
        for _pairing in self._state_refresh_pairings:
            _datapoint_id, _datapoint_value = self.get_output_by_pairing(
                pairing=_pairing
            )

            _datapoint = (
                await self.device.api.get_datapoint(
                    device_serial=self.device_serial,
                    channel_id=self.channel_id,
                    datapoint=_datapoint_id,
                )
            )[0]

            self._refresh_state_from_datapoint(
                datapoint={
                    "pairingID": _pairing.value,
                    "value": _datapoint,
                }
            )

    def _refresh_state_from_datapoints(self):
        """Refresh the state of the channel from the datapoints."""
        for _datapoint in self._outputs.values():
            self._refresh_state_from_datapoint(_datapoint)

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> str:
        """Refresh the state of the channel from a single datapoint."""

    def __repr__(self) -> str:
        """Return a string representation of the channel."""
        return (
            f"Channel(class='{self.__class__.__name__}', "
            f"channel_id='{self.channel_id}', "
            f"channel_name='{self.channel_name}', "
            f"room_name='{self.room_name}')"
        )
