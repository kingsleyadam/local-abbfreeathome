"""ABB-Free@Home wrapper for interacting with the ABB-free@home API."""

from .api import FreeAtHomeApi
from .bin.function_id import FunctionID
from .devices.switch import Switch


class FreeAtHome:
    """Provides a class for interacting with the ABB-free@home API."""

    _config = None

    def __init__(self, api: FreeAtHomeApi) -> None:
        """Initialize the FreeAtHome class."""
        self._api = api

    @property
    async def floors(self) -> dict:
        """Get the floors from the configuration."""
        return (await self.get_config()).get("floorplan").get("floors")

    async def get_config(self, refresh: bool = False) -> dict:
        """Get the Free@Home Configuration."""
        if self._config is None or refresh:
            self._config = await self._api.get_configuration()

        return self._config

    async def get_devices_by_function(self, function_id: str) -> list[dict]:
        """Get the list of devices by function."""
        _devices = []
        for _device_key, _device in (await self.get_config()).get("devices").items():
            for _channel_key, _channel in _device.get("channels", {}).items():
                if _channel.get("functionID") == function_id:
                    _channel_name = _channel.get("displayName")
                    if _channel_name == "Ⓐ" or _channel_name is None:
                        _channel_name = _device.get("displayName")

                    _devices.append(
                        {
                            "device_id": _device_key,
                            "device_name": _device.get("displayName"),
                            "channel_id": _channel_key,
                            "channel_name": _channel_name,
                            "function_id": _channel.get("functionID"),
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

    async def get_floor_name(self, floor_serial_id: str) -> str:
        """Get the floor name from the configuration."""
        _default_room = {"name": "unknown", "rooms": {}}
        return (await self.floors).get(floor_serial_id, _default_room).get("name")

    async def get_room_name(self, floor_serial_id: str, room_serial_id: str) -> str:
        """Get the room name from the configuration."""
        _default_room = {"name": "unknown", "rooms": {}}
        return (
            (await self.floors)
            .get(floor_serial_id, _default_room)
            .get("rooms")
            .get(room_serial_id)
            .get("name", "unknown")
        )

    async def get_switches(self) -> list[Switch]:
        """Get the list of switch devices."""
        _switch_devices = await self.get_devices_by_function(
            function_id=FunctionID.FID_SWITCH_ACTUATOR.value
        )
        return [
            Switch(
                device_id=_device.get("device_id"),
                device_name=_device.get("device_name"),
                channel_id=_device.get("channel_id"),
                channel_name=_device.get("channel_name"),
                inputs=_device.get("inputs"),
                outputs=_device.get("outputs"),
                parameters=_device.get("parameters"),
                api=self._api,
            )
            for _device in _switch_devices
        ]


if __name__ == "__main__":
    pass
