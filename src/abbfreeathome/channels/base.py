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
from ..parameters import ParametersMixin

if TYPE_CHECKING:
    from ..device import Device

_LOGGER = logging.getLogger(__name__)


class Base(ParametersMixin):
    """Free@Home Base Class."""

    _state_refresh_pairings: list[Pairing] = []
    # Input pairings to load at construction and fetch in refresh_state().
    _input_refresh_pairings: list[Pairing] = []
    _callback_attributes: list[str] = []
    # Callback attributes that report commands rather than state, such as a
    # sensor's button press or a request sent to an actuator. refresh_state()
    # updates them without notifying, so a refresh does not look like a command.
    _command_callback_attributes: list[str] = []
    # Also refresh state from input (idp) datapoint updates. Physical channels
    # report confirmed state on outputs, and inputs carry commands that may
    # share a pairing ID with an output (e.g. MWire switch actuators), so this
    # is off by default. Enable it for virtual channels, whose inputs carry
    # commands from the SysAP, and for channels exposing requested values.
    _handle_input_updates: bool = False

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

    def update_location(self, floor_name: str | None, room_name: str | None) -> None:
        """Update resolved location names without replacing the channel."""
        self._floor_name = floor_name
        self._room_name = room_name

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

    def update_channel(
        self, datapoint_key: str, datapoint_value: str, is_priming: bool = False
    ):
        """
        Update the channel state.

        When ``is_priming`` is True the incoming datapoint is part of a
        post-(re)connect snapshot replay. The cache is always updated so it
        stays consistent with the gateway, but callbacks are suppressed for
        datapoints whose value did not change -- preventing the phantom
        callback flood (issue #239) while still surfacing datapoints that
        genuinely changed while the connection was down.

        Output datapoints are always handled; input datapoints only when the
        channel sets ``_handle_input_updates``.
        """
        _LOGGER.info(
            "%s received updated data: %s: %s",
            self.channel_name,
            datapoint_key,
            datapoint_value,
        )
        _callback_attributes: list[str] = []
        _changed = True
        _io_key = datapoint_key.rsplit("/", maxsplit=1)[-1]

        _datapoints = self._outputs
        if _io_key not in _datapoints and self._handle_input_updates:
            _datapoints = self._inputs

        if _io_key in _datapoints:
            _changed = _datapoints[_io_key].get("value") != datapoint_value
            _datapoints[_io_key]["value"] = datapoint_value
            _callback_attributes = self._refresh_state_from_datapoint(
                datapoint=_datapoints[_io_key]
            )

        if is_priming and not _changed:
            return

        self._notify_callbacks(_callback_attributes)

    def _notify_callbacks(self, attributes: list[str]) -> None:
        """Notify each subscriber once for the refreshed attributes."""
        callbacks = {
            callback
            for attribute in attributes
            for callback in self._callbacks.get(attribute, ())
        }
        for callback in callbacks:
            try:
                callback()
            except Exception:  # noqa: BLE001
                _LOGGER.exception(
                    "Error in callback for %s/%s", self.device_serial, self.channel_id
                )

    def update_scene(
        self, datapoint_key: str, datapoint_value: str, is_priming: bool = False
    ):
        """Update an output reported by a triggered scene."""
        self.update_channel(datapoint_key, datapoint_value, is_priming=is_priming)

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
        """
        Refresh the state of the channel from the api.

        The values read replace the cached datapoint values, except where a
        WebSocket update changed a datapoint while its request was pending.
        Afterwards, even if a request fails, each subscriber of a refreshed
        attribute is notified once, except for ``_command_callback_attributes``.
        """
        _callback_attributes: list[str] = []
        try:
            for _pairing in self._state_refresh_pairings:
                _datapoint_id, _ = self.get_output_by_pairing(pairing=_pairing)
                _callback_attributes += await self._refresh_datapoint(
                    _datapoint_id, self._outputs[_datapoint_id]
                )

            for _datapoint_id, _datapoint in self._input_refresh_datapoints():
                _callback_attributes += await self._refresh_datapoint(
                    _datapoint_id, _datapoint
                )
        finally:
            # Callback errors are logged by _notify_callbacks(), so they cannot
            # replace an exception raised by a request.
            self._notify_callbacks(
                [
                    _attribute
                    for _attribute in _callback_attributes
                    if _attribute not in self._command_callback_attributes
                ]
            )

    async def _refresh_datapoint(
        self, datapoint_id: str, datapoint: dict[str, Any]
    ) -> list[str]:
        """Read a datapoint into the cache and return the affected attributes."""
        _cached_value = datapoint.get("value")
        _value = (
            await self.device.api.get_datapoint(
                device_serial=self.device_serial,
                channel_id=self.channel_id,
                datapoint=datapoint_id,
            )
        )[0]

        # A WebSocket update received during the request is newer; keep it.
        if datapoint.get("value") != _cached_value:
            return []

        datapoint["value"] = _value
        return self._refresh_state_from_datapoint(datapoint=datapoint)

    def _refresh_state_from_datapoints(self):
        """Refresh the state of the channel from the datapoints."""
        for _datapoint in self._outputs.values():
            self._refresh_state_from_datapoint(_datapoint)

        for _datapoint_id, _datapoint in self._input_refresh_datapoints():
            self._refresh_state_from_datapoint(_datapoint)

    def _input_refresh_datapoints(self) -> list[tuple[str, dict[str, Any]]]:
        """Return the inputs matching ``_input_refresh_pairings``."""
        _pairings = {_pairing.value for _pairing in self._input_refresh_pairings}
        return [
            (_datapoint_id, _datapoint)
            for _datapoint_id, _datapoint in self._inputs.items()
            if _datapoint.get("pairingID") in _pairings
        ]

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> list[str]:
        """Refresh state and return affected attribute names, or an empty list."""
        return []

    def __repr__(self) -> str:
        """Return a string representation of the channel."""
        return (
            f"Channel(class='{self.__class__.__name__}', "
            f"channel_id='{self.channel_id}', "
            f"channel_name='{self.channel_name}', "
            f"room_name='{self.room_name}')"
        )
