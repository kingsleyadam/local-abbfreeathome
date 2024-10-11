"""ABB-Free@Home wrapper for interacting with the ABB-free@home API."""

from .api import FreeAtHomeApi
from .bin.function_id import FunctionID
from .bin.interface import Interface
from .devices.switch_actuator import Base, SwitchActuator


class FreeAtHome:
    """Provides a class for interacting with the ABB-free@home API."""

    _config = None
    _devices = {}

    def __init__(
        self, api: FreeAtHomeApi, interfaces: list[Interface] | None = None
    ) -> None:
        """Initialize the FreeAtHome class."""
        self._api = api
        self._interfaces = interfaces

    async def get_config(self, refresh: bool = False) -> dict:
        """Get the Free@Home Configuration."""
        if self._config is None or refresh:
            self._config = await self._api.get_configuration()

        return self._config

    async def get_devices_by_function(self, function_id: FunctionID) -> list[dict]:
        """Get the list of devices by function."""
        _devices = []
        for _device_key, _device in (await self.get_config()).get("devices").items():
            # Filter by interface if provided
            if self._interfaces and _device.get("interface") not in [
                interface.value for interface in self._interfaces
            ]:
                continue

            for _channel_key, _channel in _device.get("channels", {}).items():
                if (
                    _channel.get("functionID")
                    and int(_channel.get("functionID"), 16) == function_id.value
                ):
                    _channel_name = _channel.get("displayName")
                    if _channel_name == "Ⓐ" or _channel_name is None:
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

    def get_device_by_class(self, device_class: Base) -> list[Base]:
        """Get the list of devices by class."""
        return [
            _device
            for _device in self._devices.values()
            if isinstance(_device, device_class)
        ]

    async def load_devices(self):
        """Load all of the devices into the device list."""
        await self._load_switches()

    async def _load_switches(self):
        _switch_devices = await self.get_devices_by_function(
            function_id=FunctionID.FID_SWITCH_ACTUATOR
        )
        for _device in _switch_devices:
            self._devices[f"{_device.get("device_id")}/{_device.get("channel_id")}"] = (
                SwitchActuator(
                    device_id=_device.get("device_id"),
                    device_name=_device.get("device_name"),
                    channel_id=_device.get("channel_id"),
                    channel_name=_device.get("channel_name"),
                    inputs=_device.get("inputs"),
                    outputs=_device.get("outputs"),
                    parameters=_device.get("parameters"),
                    api=self._api,
                    floor_name=_device.get("floor_name"),
                    room_name=_device.get("room_name"),
                )
            )

    async def ws_close(self):
        """Close the websocker connection."""
        await self._api.ws_close()

    async def ws_listen(self):
        """Listen on the websocket for updates to devices."""
        await self._api.ws_listen(callback=self.update_device)

    async def update_device(self, data: dict):
        """Update device based on websocket data."""
        for _datapoint_key, _datapoint_value in data.get("datapoints").items():
            _unique_id = "/".join(_datapoint_key.split("/")[:-1])
            try:
                _device = self._devices[_unique_id]
                _device.update_device(_datapoint_key, _datapoint_value)
            except KeyError:
                continue
