"""ABB-Free@Home wrapper for interacting with the ABB-free@home API."""

from .api import FreeAtHomeApi
from .bin.function import Function
from .bin.interface import Interface
from .channels.base import Base
from .const import FUNCTION_CHANNEL_MAPPING, FUNCTION_VIRTUAL_CHANNEL_MAPPING
from .device import Device


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
        self._channels: dict[str, Base] = {}
        self._devices: dict[str, Device] = {}

        self.api: FreeAtHomeApi = api

        self._interfaces: list[Interface] | None = interfaces
        self._channel_classes: list[type[Base]] | None = channel_classes
        self._include_orphan_channels: bool = include_orphan_channels

    def clear_channels(self):
        """Clear all channels in the channels list."""
        self._channels.clear()

    def clear_devices(self):
        """Clear all devices in the devices list."""
        self._devices.clear()

    async def get_config(self, refresh: bool = False) -> dict:
        """Get the Free@Home Configuration."""
        if self._config is None or refresh:
            self._config = await self.api.get_configuration()

        return self._config

    def get_channels(self) -> dict[str, Base]:
        """Get the list of channels."""
        return self._channels

    def get_devices(self) -> dict[str, Device]:
        """Get the list of devices."""
        return self._devices

    def get_device_by_serial(self, device_serial: str) -> Device | None:
        """Get a device by its serial ID."""
        return self._devices.get(device_serial)

    def get_device_for_channel(self, channel_key: str) -> Device | None:
        """Get the device that contains a specific channel."""
        device_serial = channel_key.split("/")[0]
        return self.get_device_by_serial(device_serial)

    def get_channels_by_class(self, channel_class: Base) -> list[Base]:
        """Get the list of channels by class."""
        return [
            _channel
            for _channel in self._channels.values()
            if type(_channel) is channel_class
        ]

    async def get_channels_by_function(self, function: Function) -> list[dict]:
        """Get the list of channels by function."""
        # Ensure devices are loaded
        if not self._devices:
            await self._load_devices()

        _channels = []
        for _device_key, _device in self._devices.items():
            # Filter by interface if provided
            if self._interfaces and _device.interface not in self._interfaces:
                continue

            for _channel_key, _channel in _device.channels.items():
                # Filter out any channels not on the Free@Home floorplan
                if (
                    not self._include_orphan_channels
                    and not _channel.get("floor")
                    and not _channel.get("room")
                ):
                    continue

                if (
                    _channel.get("functionID")
                    and int(_channel.get("functionID"), 16) == function.value
                ):
                    _channel_name = _channel.get("displayName")
                    if _channel_name in ["Ⓐ", "ⓑ"] or _channel_name is None:
                        _channel_name = _device.display_name

                    _channels.append(
                        {
                            "device_serial": _device_key,
                            "device_name": _device.display_name,
                            "channel_id": _channel_key,
                            "channel_name": _channel_name,
                            "function_id": int(_channel.get("functionID"), 16),
                            "floor_name": _device.floor_name
                            or await self.get_floor_name(
                                floor_serial_id=_channel.get("floor", _device.floor)
                            ),
                            "room_name": _device.room_name
                            or await self.get_room_name(
                                floor_serial_id=_channel.get("floor", _device.floor),
                                room_serial_id=_channel.get("room", _device.room),
                            ),
                            "inputs": _channel.get("inputs"),
                            "outputs": _channel.get("outputs"),
                            "parameters": _channel.get("parameters"),
                            "virtual": _device.is_virtual,
                        }
                    )

        return _channels

    async def get_floors(self) -> dict:
        """Get the floors from the configuration."""
        return (await self.get_config()).get("floorplan").get("floors")

    async def get_floor_name(self, floor_serial_id: str) -> str | None:
        """Get the floor name from the configuration."""
        _default_floor = {"name": None}

        return (
            (await self.get_floors()).get(floor_serial_id, _default_floor).get("name")
        )

    async def get_room_name(
        self, floor_serial_id: str, room_serial_id: str
    ) -> str | None:
        """Get the room name from the configuration."""
        _default_floor = {"name": None, "rooms": {}}
        _default_room = {"name": None}

        return (
            (await self.get_floors())
            .get(floor_serial_id, _default_floor)
            .get("rooms")
            .get(room_serial_id, _default_room)
            .get("name")
        )

    async def load(self):
        """Load from the Free@Home api into the FreeAtHome class."""
        await self._load_devices()
        await self._load_channels()

    async def _load_devices(self):
        """Load all devices into the devices object."""
        self.clear_devices()

        _config = await self.get_config()
        for _serial, _data in _config.get("devices", {}).items():
            # Convert interface string to Interface enum
            _interface_value = _data.get("interface")

            # Any devices that start with "6000" should be considered virtual
            if _serial.startswith("6000"):
                _interface_value = "VD"

            _interface = Interface.from_string(_interface_value)

            # Get floor and room names
            _floor_id = _data.get("floor")
            _room_id = _data.get("room")
            _floor_name = await self.get_floor_name(_floor_id) if _floor_id else None
            _room_name = (
                await self.get_room_name(_floor_id, _room_id)
                if _floor_id and _room_id
                else None
            )

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
                channels=_data.get("channels", {}),
            )

            self._devices[_serial] = _device

    async def _load_channels(self):
        """Load all of the channels into the channels object."""
        self.clear_channels()
        for _virtual_channel in (False, True):
            for _function, _function_class in self._get_function_to_channel_mapping(
                virtual_channel=_virtual_channel
            ).items():
                await self._load_channels_by_function(
                    function=_function,
                    channel_class=_function_class,
                    virtual_channel=_virtual_channel,
                )

    def unload_channel_by_channel_serial(self, channel_serial: str):
        """Unload all channels by channel serial id."""
        for key in [
            _channel
            for _channel in self._channels
            if _channel.split("/")[0] == channel_serial
        ]:
            self._channels.pop(key)

    def unload_device_by_serial(self, device_serial: str):
        """Unload a device by its serial ID."""
        if device_serial in self._devices:
            self._devices.pop(device_serial)

    async def _load_channels_by_function(
        self,
        function: Function,
        channel_class: Base,
        virtual_channel: bool = False,
    ):
        _channels = await self.get_channels_by_function(function)

        for _channel in _channels:
            if (_channel.get("virtual") is False and virtual_channel) or (
                _channel.get("virtual") and not virtual_channel
            ):
                continue

            self._channels[
                f"{_channel.get('device_serial')}/{_channel.get('channel_id')}"
            ] = channel_class(
                device_serial=_channel.get("device_serial"),
                device_name=_channel.get("device_name"),
                channel_id=_channel.get("channel_id"),
                channel_name=_channel.get("channel_name"),
                inputs=_channel.get("inputs"),
                outputs=_channel.get("outputs"),
                parameters=_channel.get("parameters"),
                api=self.api,
                floor_name=_channel.get("floor_name"),
                room_name=_channel.get("room_name"),
            )

    async def ws_close(self):
        """Close the websocker connection."""
        await self.api.ws_close()

    async def ws_listen(self):
        """Listen on the websocket for updates to Free@Home objects."""
        await self.api.ws_listen(callback=self.update)

    async def update(self, data: dict):
        """Update channel based on websocket data."""
        for _datapoint_key, _datapoint_value in data.get("datapoints").items():
            _unique_id = "/".join(_datapoint_key.split("/")[:-1])
            try:
                _channel = self._channels[_unique_id]
                _channel.update_channel(_datapoint_key, _datapoint_value)
            except KeyError:
                continue

    def _get_function_to_channel_mapping(
        self, virtual_channel: bool = False
    ) -> dict[Function, Base]:
        _channel_mapping = (
            FUNCTION_VIRTUAL_CHANNEL_MAPPING
            if virtual_channel
            else FUNCTION_CHANNEL_MAPPING
        )

        return (
            _channel_mapping
            if not self._channel_classes
            else {
                key: value
                for key, value in _channel_mapping.items()
                if value in self._channel_classes
            }
        )
