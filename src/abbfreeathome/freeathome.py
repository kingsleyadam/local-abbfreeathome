"""ABB-Free@Home wrapper for interacting with the ABB-free@home API."""

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
import logging

from .api import FreeAtHomeApi
from .bin.interface import Interface
from .channels.base import Base
from .device import Device, copy_locations
from .exceptions import InvalidDeviceChannelPairing
from .floorplan import Floorplan

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DevicesChangedEvent:
    """Describe exact device additions and newly visible, filtered channels."""

    added_devices: tuple[Device, ...] = ()
    added_channels: tuple[Base, ...] = ()
    removed_device_serials: tuple[str, ...] = ()


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
        self._devices_changed_callbacks: set[Callable[[DevicesChangedEvent], None]] = (
            set()
        )

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

    def register_devices_changed_callback(
        self, callback: Callable[[DevicesChangedEvent], None]
    ) -> None:
        """Subscribe to explicit discovery events after state updates."""
        self._devices_changed_callbacks.add(callback)

    def remove_devices_changed_callback(
        self, callback: Callable[[DevicesChangedEvent], None]
    ) -> None:
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
        _added_devices = await self._update_devices(data)
        _channels = self.get_channels()
        _added_channels = (
            ()
            if _channels is _previous_channels
            else tuple(
                _channel
                for _key, _channel in _channels.items()
                if _key not in _previous_channels
            )
        )

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

        _datapoints = dict(data.get("datapoints") or {})
        _datapoints.update(_scene_datapoints)

        for _datapoint_key, _datapoint_value in _datapoints.items():
            _unique_id = "/".join(_datapoint_key.split("/")[:-1])

            # Filtered-out channels are kept current so they are ready if placed.
            _channel = _channels.get(_unique_id)
            if _channel is None:
                _serial, _, _channel_id = _unique_id.partition("/")
                _device = self._devices.get(_serial)
                if _device is None:
                    continue
                _channel = _device.channels.get(_channel_id)
                if _channel is None:
                    continue

            if _datapoint_key in _scene_datapoints:
                _channel.update_scene(
                    _datapoint_key, _datapoint_value, is_priming=_is_priming
                )
            else:
                _channel.update_channel(
                    _datapoint_key, _datapoint_value, is_priming=_is_priming
                )

        if _added_devices or _added_channels:
            _event = DevicesChangedEvent(
                added_devices=_added_devices, added_channels=_added_channels
            )
            for _callback in tuple(self._devices_changed_callbacks):
                _callback(_event)

    async def _update_devices(self, data: dict) -> tuple[Device, ...]:
        _added_devices = await self._add_devices(data)
        _device_updates = data.get("devices") or {}
        if not _device_updates:
            return _added_devices

        _floorplan = Floorplan.from_config(self._config or {})
        _cached_devices = (self._config or {}).get("devices", {})
        for _serial, _device_data in _device_updates.items():
            _device = self._devices.get(_serial)
            if _device is None or not isinstance(_device_data, dict):
                continue
            _device.update_locations(_device_data, _floorplan)
            # Keep a refreshed config cache in sync with explicit locations.
            _cached = _cached_devices.get(_serial)
            if _cached is not None:
                copy_locations(_cached, _device_data)
                _channel_updates = _device_data.get("channels") or {}
                for _channel_id, _update in _channel_updates.items():
                    _cached_channel = (_cached.get("channels") or {}).get(_channel_id)
                    if isinstance(_update, dict) and isinstance(_cached_channel, dict):
                        copy_locations(_cached_channel, _update)
            self._filtered_channels = None
        return _added_devices

    async def _add_devices(self, data: dict) -> tuple[Device, ...]:
        _added = data.get("devicesAdded") or []
        if not _added:
            return ()
        if not isinstance(_added, list):
            _LOGGER.error("Ignoring invalid devicesAdded: %r", _added)
            return ()
        _config = await self.get_config()
        _floorplan = Floorplan.from_config(_config)
        _added_devices = []
        for _serial in _added:
            if not isinstance(_serial, str):
                _LOGGER.error("Ignoring invalid devicesAdded entry: %r", _serial)
                continue
            if _serial in self._devices:
                continue
            _device_data = (data.get("devices") or {}).get(_serial)
            if not isinstance(_device_data, dict):
                _LOGGER.error(
                    "Cannot add device %s: missing device configuration", _serial
                )
                continue
            _device_data = deepcopy(_device_data)
            try:
                _device = self._create_device(_serial, _device_data, _floorplan)
            except (
                AttributeError,
                KeyError,
                OverflowError,
                TypeError,
                ValueError,
                InvalidDeviceChannelPairing,
            ):
                _LOGGER.exception("Cannot initialize added device %s", _serial)
                continue
            if _device is not None and not all(
                isinstance(_section.get("parameters", {}), dict)
                for _section in (
                    _device_data,
                    *(_device_data.get("channels") or {}).values(),
                )
            ):
                _LOGGER.error("Cannot add device %s: invalid parameters", _serial)
                continue
            _config.setdefault("devices", {})[_serial] = _device_data
            if _device is not None:
                self._devices[_serial] = _device
                self._filtered_channels = None
                _added_devices.append(_device)

        return tuple(_added_devices)

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
