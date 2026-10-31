"""ABB-Free@Home wrapper for interacting with the ABB-free@home API."""

from collections.abc import Callable
from copy import deepcopy
import logging

from .api import FreeAtHomeApi
from .bin.interface import Interface
from .channels.base import Base
from .device import Device
from .exceptions import InvalidDeviceChannelPairing
from .floorplan import Floorplan

_LOGGER = logging.getLogger(__name__)


class FreeAtHome:
    """Provides a class for interacting with the ABB-free@home API."""

    def __init__(
        self,
        api: FreeAtHomeApi,
        interfaces: list[Interface] | None = None,
        channel_classes: list[type[Base]] | None = None,
        include_orphan_channels: bool = False,
    ) -> None:
        """Initialize the FreeAtHome class."""
        self._config: dict | None = None
        self._devices: dict[str, Device] = {}
        self._filtered_channels: dict[str, Base] | None = None
        self._devices_changed_callbacks: set[Callable[[], None]] = set()

        self.api: FreeAtHomeApi = api

        self._interfaces: list[Interface] | None = interfaces
        self._channel_classes: list[type[Base]] | None = channel_classes
        self._include_orphan_channels: bool = include_orphan_channels

    def clear_channels(self):
        """Clear all channels in the devices."""
        for device in self._devices.values():
            device.clear_channels()
        self._filtered_channels = None

    def clear_devices(self):
        """Clear all devices in the devices list."""
        self._devices.clear()
        self._filtered_channels = None

    def get_channels(self) -> dict[str, Base]:
        """Get channels from all devices based on class filters."""
        if self._filtered_channels is None:
            self._filtered_channels = self._build_filtered_channels()
        return self._filtered_channels

    def get_channels_by_device(self, device_serial: str) -> list[Base]:
        """Get the list of channels by device."""
        _channels = self.get_channels()
        return [
            _channel
            for key, _channel in _channels.items()
            if key.startswith(f"{device_serial}/")
        ]

    def get_channels_by_class(self, channel_class: Base) -> list[Base]:
        """Get the list of channels by class."""
        _channels = self.get_channels()
        return [
            _channel
            for _channel in _channels.values()
            if type(_channel) is channel_class
        ]

    async def get_config(self, refresh: bool = False) -> dict:
        """Get the Free@Home Configuration."""
        if self._config is None or refresh:
            self._config = await self.api.get_configuration()

        return self._config

    def get_device_by_serial(self, device_serial: str) -> Device | None:
        """Get a device by its serial ID."""
        return self._devices.get(device_serial)

    def get_devices(self) -> dict[str, Device]:
        """Get the list of devices."""
        return self._devices

    async def load(self):
        """Load from the Free@Home api into the FreeAtHome class."""
        await self._load_devices()

    def register_devices_changed_callback(self, callback: Callable[[], None]) -> None:
        """Subscribe to additions and newly eligible channels after state updates."""
        self._devices_changed_callbacks.add(callback)

    def remove_devices_changed_callback(self, callback: Callable[[], None]) -> None:
        """Remove a discovery subscription."""
        self._devices_changed_callbacks.discard(callback)

    def unload_channel(self, device_serial: str, channel_id: str):
        """Unload a specific channel by device serial and channel id."""
        try:
            _device = self._devices[device_serial]
            _device.channels.pop(channel_id)

            # Invalidate the filtered channels cache
            self._filtered_channels = None
        except KeyError:
            pass

    def unload_device(self, device_serial: str):
        """Unload a device by its serial ID."""
        try:
            self._devices.pop(device_serial)

            # Invalidate the filtered channels cache
            self._filtered_channels = None
        except KeyError:
            pass

    async def update(self, data: dict):
        """Update channel based on websocket data."""
        _previous_channels = self.get_channels()
        _devices_changed = await self._update_devices(data)
        _channels = self.get_channels()

        # Datapoints received during the post-(re)connect priming window are a
        # replayed snapshot, not real events: update caches but skip callbacks.
        _is_priming = self.api.is_priming

        # Parameters first: channels read them (e.g. LED mode) to interpret
        # datapoints arriving in the same message.
        self._update_parameters(data)

        # Scene output values use a nested structure instead of datapoint paths.
        # Merge them into a copy so each datapoint is dispatched only once.
        _scene_datapoints = {}
        for _serial, _device in (data.get("scenesTriggered") or {}).items():
            for _channel_id, _channel_data in (_device.get("channels") or {}).items():
                for _output_id, _output in (_channel_data.get("outputs") or {}).items():
                    _datapoint_key = f"{_serial}/{_channel_id}/{_output_id}"
                    _scene_datapoints[_datapoint_key] = _output["value"]

        # A newly placed channel may have missed updates while filtered out.
        _datapoints = self._get_discovery_datapoints(
            data, _channels.keys() - _previous_channels.keys()
        )
        _datapoints.update(data.get("datapoints") or {})
        _datapoints.update(_scene_datapoints)

        for _datapoint_key, _datapoint_value in _datapoints.items():
            _unique_id = "/".join(_datapoint_key.split("/")[:-1])

            try:
                _channel = _channels[_unique_id]
                if _datapoint_key in _scene_datapoints:
                    _channel.update_scene(
                        _datapoint_key, _datapoint_value, is_priming=_is_priming
                    )
                else:
                    _channel.update_channel(
                        _datapoint_key, _datapoint_value, is_priming=_is_priming
                    )
            except KeyError:
                continue

        if _devices_changed:
            for _callback in tuple(self._devices_changed_callbacks):
                _callback()

    async def _update_devices(self, data: dict) -> bool:
        _device_updates = data.get("devices") or {}
        if not _device_updates and not data.get("devicesAdded"):
            return False

        _changed = await self._add_devices(data)
        _floorplan = Floorplan.from_config(self._config or {})
        for _serial, _device_data in _device_updates.items():
            _device = self._devices.get(_serial)
            if _device is None or not isinstance(_device_data, dict):
                continue
            _previous_channels = self.get_channels()
            if _device.update_locations(_device_data, _floorplan):
                if self._config is not None:
                    _cached = self._config.setdefault("devices", {}).setdefault(
                        _serial, {}
                    )
                    for _key in ("floor", "room"):
                        if _key in _device_data:
                            _cached[_key] = _device_data[_key]
                    for _channel_id, _channel_data in _device.channels_data.items():
                        _cached_channel = _cached.setdefault("channels", {}).setdefault(
                            _channel_id, {}
                        )
                        for _key in ("floor", "room"):
                            if _key in _channel_data:
                                _cached_channel[_key] = _channel_data[_key]
                self._filtered_channels = None
                _changed |= bool(self.get_channels().keys() - _previous_channels.keys())
        return _changed

    async def _add_devices(self, data: dict) -> bool:
        _added = data.get("devicesAdded") or []
        if not _added:
            return False
        _config = await self.get_config()
        _floorplan = Floorplan.from_config(_config)
        _changed = False
        for _serial in _added:
            if _serial in self._devices:
                continue
            _device_data = (data.get("devices") or {}).get(_serial)
            if not isinstance(_device_data, dict) or not self._valid_device_config(
                _device_data
            ):
                _LOGGER.error(
                    "Cannot add device %s: missing or invalid device configuration",
                    _serial,
                )
                continue
            _device_data = deepcopy(_device_data)
            try:
                _device = self._create_device(_serial, _device_data, _floorplan)
            except (
                AttributeError,
                KeyError,
                TypeError,
                ValueError,
                InvalidDeviceChannelPairing,
            ):
                _LOGGER.exception("Cannot initialize added device %s", _serial)
                continue
            _config.setdefault("devices", {})[_serial] = _device_data
            if _device is not None:
                self._devices[_serial] = _device
                self._filtered_channels = None
                _changed = True

        return _changed

    @staticmethod
    def _valid_device_config(data: dict) -> bool:
        _channels = data.get("channels")
        if not isinstance(_channels, dict) or any(
            not isinstance(_channel, dict) for _channel in _channels.values()
        ):
            return False
        for _section in (data, *_channels.values()):
            if not isinstance(_section.get("parameters", {}), dict):
                return False
            if any(
                _section.get(_key) is not None and not isinstance(_section[_key], str)
                for _key in ("floor", "room")
            ):
                return False
        for _channel in _channels.values():
            _function_id = _channel.get("functionID")
            if _function_id:
                try:
                    int(_function_id, 16)
                except (TypeError, ValueError):
                    return False
            for _direction in ("inputs", "outputs"):
                _datapoints = _channel.get(_direction, {})
                if not isinstance(_datapoints, dict) or any(
                    not isinstance(_point, dict)
                    or "value" not in _point
                    or not isinstance(_point.get("pairingID"), int)
                    for _point in _datapoints.values()
                ):
                    return False
        return True

    @staticmethod
    def _get_discovery_datapoints(data: dict, channel_ids: set[str]) -> dict:
        _datapoints = {}
        for _unique_id in channel_ids:
            _serial, _channel_id = _unique_id.split("/")
            _channel_data = (
                (data.get("devices") or {})
                .get(_serial, {})
                .get("channels", {})
                .get(_channel_id, {})
            )
            for _output_id, _output in (_channel_data.get("outputs") or {}).items():
                _datapoints[f"{_unique_id}/{_output_id}"] = _output.get("value")
        return _datapoints

    def _update_parameters(self, data: dict) -> None:
        """Apply parameter changes from a websocket message."""
        # Changed device config is sent in full under "devices".
        for _serial, _device_data in (data.get("devices") or {}).items():
            _device = self._devices.get(_serial)
            if _device is None or not isinstance(_device_data, dict):
                continue

            self._apply_parameters(_device, _device_data.get("parameters"))
            for _channel_id, _channel_data in (
                _device_data.get("channels") or {}
            ).items():
                _channel = _device.channels.get(_channel_id)
                if _channel is not None and isinstance(_channel_data, dict):
                    self._apply_parameters(_channel, _channel_data.get("parameters"))

        # Individual parameter changes: "<serial>[/<channel>]/<parameter>".
        for _key, _value in (data.get("parameters") or {}).items():
            _parts = _key.split("/")
            _device = self._devices.get(_parts[0])
            if _device is None or len(_parts) not in (2, 3):
                continue

            _target = _device
            if len(_parts) == 3:
                _target = _device.channels.get(_parts[1])
            if _target is not None:
                _target.update_parameter(_parts[-1], _value)

    @staticmethod
    def _apply_parameters(target, parameters: dict | None) -> None:
        for _parameter_id, _value in (parameters or {}).items():
            target.update_parameter(_parameter_id, _value)

    async def ws_close(self):
        """Close the websocket connection."""
        await self.api.ws_close()

    async def ws_listen(self):
        """Listen on the websocket for updates to Free@Home objects."""
        await self.api.ws_listen(callback=self.update)

    def _build_filtered_channels(self) -> dict[str, Base]:
        """Build a filtered dictionary of channels based on current filters."""
        _all_channels = {}

        for device_serial, device in self._devices.items():
            for channel_id, channel_data in device.channels_data.items():
                # Filter out any channels not on the Free@Home floorplan
                if (
                    not self._include_orphan_channels
                    and not channel_data.get("floor")
                    and not channel_data.get("room")
                ):
                    continue

                # Get the actual Channel object from device.channels
                device_channels = device.channels
                if channel_id not in device_channels:
                    continue

                channel = device_channels[channel_id]

                # Filter by channel class if provided
                if self._channel_classes and type(channel) not in self._channel_classes:
                    continue

                # Use the same key format as before: "device_serial/channel_id"
                channel_serial = f"{device_serial}/{channel_id}"
                _all_channels[channel_serial] = channel

        return _all_channels

    async def _load_devices(self):
        """Load all devices into the devices object."""
        self.clear_devices()

        _config = await self.get_config()

        # Create floor plan from configuration
        _floorplan = Floorplan.from_config(_config)

        for _serial, _data in _config.get("devices", {}).items():
            _device = self._create_device(_serial, _data, _floorplan)
            if _device is not None:
                self._devices[_serial] = _device

        # Invalidate the filtered channels cache after loading devices
        self._filtered_channels = None

    def _create_device(
        self, serial: str, data: dict, floorplan: Floorplan
    ) -> Device | None:
        _interface = Interface.from_string(
            "VD" if serial.startswith("6000") else data.get("interface")
        )
        if self._interfaces and _interface not in self._interfaces:
            return None

        _floor = data.get("floor")
        _room = data.get("room")
        _device = Device(
            device_serial=serial,
            device_id=data.get("deviceId", ""),
            display_name=data.get("displayName", ""),
            interface=_interface,
            unresponsive=data.get("unresponsive", False),
            unresponsive_counter=data.get("unresponsiveCounter", 0),
            defect=data.get("defect", False),
            floor=_floor,
            room=_room,
            floor_name=floorplan.get_floor_name(_floor),
            room_name=floorplan.get_room_name(_floor, _room),
            device_reboots=data.get("deviceReboots"),
            native_id=data.get("nativeId"),
            parameters=data.get("parameters", {}),
            channels_data=data.get("channels", {}),
            api=self.api,
        )
        _device.load_channels(floorplan=floorplan)
        return _device
