"""ABB-Free@Home wrapper for interacting with the ABB-free@home API."""

from .api import FreeAtHomeApi
from .bin.interface import Interface
from .channels.base import Base
from .device import Device
from .floorplan import Floorplan


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
        _channels = self.get_channels()

        for _datapoint_key, _datapoint_value in data.get("datapoints").items():
            _unique_id = "/".join(_datapoint_key.split("/")[:-1])

            try:
                _channel = _channels[_unique_id]
                _channel.update_channel(_datapoint_key, _datapoint_value)
            except KeyError:
                continue

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
            # Convert interface string to Interface enum
            _interface_value = _data.get("interface")

            # Any devices that start with "6000" should be considered virtual
            if _serial.startswith("6000"):
                _interface_value = "VD"

            _interface = Interface.from_string(_interface_value)

            # Filter by interface if provided - skip devices not in the interface filter
            if self._interfaces and _interface not in self._interfaces:
                continue

            # Get floor and room names using floor plan
            _floor_id = _data.get("floor")
            _room_id = _data.get("room")

            _floor_name = _floorplan.get_floor_name(_floor_id)
            _room_name = _floorplan.get_room_name(_floor_id, _room_id)

            # Extract device attributes from the configuration
            _device = Device(
                device_serial=_serial,
                device_id=_data.get("deviceId", ""),
                display_name=_data.get("displayName", ""),
                interface=_interface,
                unresponsive=_data.get("unresponsive", False),
                unresponsive_counter=_data.get("unresponsiveCounter", 0),
                defect=_data.get("defect", False),
                floor=_floor_id,
                room=_room_id,
                floor_name=_floor_name,
                room_name=_room_name,
                device_reboots=_data.get("deviceReboots"),
                native_id=_data.get("nativeId"),
                parameters=_data.get("parameters", {}),
                channels_data=_data.get("channels", {}),
                api=self.api,
            )
            _device.load_channels(floorplan=_floorplan)

            self._devices[_serial] = _device

        # Invalidate the filtered channels cache after loading devices
        self._filtered_channels = None
