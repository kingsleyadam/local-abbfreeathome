"""ABB-Free@Home wrapper for interacting with the ABB-free@home API."""

from .api import FreeAtHomeApi
from .bin.function import Function
from .bin.interface import Interface
from .const import FUNCTION_DEVICE_MAPPING, FUNCTION_VIRTUAL_DEVICE_MAPPING
from .devices.base import Base


class FreeAtHome:
    """Provides a class for interacting with the ABB-free@home API."""

    def __init__(
        self,
        api: FreeAtHomeApi,
        interfaces: list[Interface] | None = None,
        device_classes: list[Base] | None = None,
        include_orphan_channels: bool = False,
    ) -> None:
        """Initialize the FreeAtHome class."""
        self._config: dict | None = None
        self._devices: dict[str, Base] = {}

        self.api: FreeAtHomeApi = api

        self._interfaces: list[Interface] = interfaces
        self._device_classes: list[Base] = device_classes
        self._include_orphan_channels: bool = include_orphan_channels

    def clear_devices(self):
        """Clear all devices in the device list."""
        self._devices.clear()

    async def get_config(self, refresh: bool = False) -> dict:
        """Get the Free@Home Configuration."""
        if self._config is None or refresh:
            self._config = await self.api.get_configuration()

        return self._config

    def get_devices(self) -> dict[str, Base]:
        """Get the list of devices."""
        return self._devices

    def get_devices_by_class(self, device_class: Base) -> list[Base]:
        """Get the list of devices by class."""
        return [
            _device
            for _device in self._devices.values()
            if type(_device) is device_class
        ]

    async def get_devices_by_function(self, function: Function) -> list[dict]:
        """Get the list of devices by function."""
        _devices = []
        for _device_key, _device in (await self.get_config()).get("devices").items():
            is_virtual = False
            if _device_key[0:4] == "6000":
                _device["interface"] = "VD"
                is_virtual = True

            # Filter by interface if provided
            if self._interfaces and _device.get("interface") not in [
                interface.value for interface in self._interfaces
            ]:
                continue

            for _channel_key, _channel in _device.get("channels", {}).items():
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
                        _channel_name = _device.get("displayName")

                    _devices.append(
                        {
                            "device_id": _device_key,
                            "device_name": _device.get("displayName"),
                            "channel_id": _channel_key,
                            "channel_name": _channel_name,
                            "function_id": int(_channel.get("functionID"), 16),
                            "floor_name": await self.get_floor_name(
                                floor_serial_id=_channel.get(
                                    "floor", _device.get("floor")
                                )
                            ),
                            "room_name": await self.get_room_name(
                                floor_serial_id=_channel.get(
                                    "floor", _device.get("floor")
                                ),
                                room_serial_id=_channel.get(
                                    "room", _device.get("room")
                                ),
                            ),
                            "inputs": _channel.get("inputs"),
                            "outputs": _channel.get("outputs"),
                            "parameters": _channel.get("parameters"),
                            "virtual": is_virtual,
                        }
                    )

        return _devices

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

    async def load_devices(self):
        """Load all of the devices into the devices object."""
        self.clear_devices()
        for _virtual_device in (False, True):
            for _function, _device_class in self._get_function_to_device_mapping(
                virtual_device=_virtual_device
            ).items():
                await self._load_devices_by_function(
                    function=_function,
                    device_class=_device_class,
                    virtual_device=_virtual_device,
                )

    def unload_device_by_device_serial(self, device_serial: str):
        """Unload all devices by device serial id."""
        for key in [
            _device
            for _device in self._devices
            if _device.split("/")[0] == device_serial
        ]:
            self._devices.pop(key)

    async def _load_devices_by_function(
        self,
        function: Function,
        device_class: Base,
        virtual_device: bool = False,
    ):
        _devices = await self.get_devices_by_function(function)

        for _device in _devices:
            if (_device.get("virtual") is False and virtual_device) or (
                _device.get("virtual") and not virtual_device
            ):
                continue

            self._devices[f"{_device.get('device_id')}/{_device.get('channel_id')}"] = (
                device_class(
                    device_id=_device.get("device_id"),
                    device_name=_device.get("device_name"),
                    channel_id=_device.get("channel_id"),
                    channel_name=_device.get("channel_name"),
                    inputs=_device.get("inputs"),
                    outputs=_device.get("outputs"),
                    parameters=_device.get("parameters"),
                    api=self.api,
                    floor_name=_device.get("floor_name"),
                    room_name=_device.get("room_name"),
                )
            )

    async def ws_close(self):
        """Close the websocker connection."""
        await self.api.ws_close()

    async def ws_listen(self):
        """Listen on the websocket for updates to devices."""
        await self.api.ws_listen(callback=self.update_device)

    async def update_device(self, data: dict):
        """Update device based on websocket data."""
        for _datapoint_key, _datapoint_value in data.get("datapoints").items():
            _unique_id = "/".join(_datapoint_key.split("/")[:-1])
            try:
                _device = self._devices[_unique_id]
                _device.update_device(_datapoint_key, _datapoint_value)
            except KeyError:
                continue

    def _get_function_to_device_mapping(
        self, virtual_device: bool = False
    ) -> dict[Function, Base]:
        _device_mapping = (
            FUNCTION_VIRTUAL_DEVICE_MAPPING
            if virtual_device
            else FUNCTION_DEVICE_MAPPING
        )

        return (
            _device_mapping
            if not self._device_classes
            else {
                key: value
                for key, value in _device_mapping.items()
                if value in self._device_classes
            }
        )
