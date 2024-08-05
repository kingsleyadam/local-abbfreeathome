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
    def floors(self) -> dict:
        """Get the floors from the configuration."""
        return self.get_config().get("floorplan").get("floors")

    @property
    def switches(self) -> list[Switch]:
        """Get the list of switche devices."""
        _switch_devices = self.get_devices_by_function(
            function_id=FunctionID.FID_SWITCH_ACTUATOR.value
        )
        return [
            Switch(
                device_id=_device.get("device_id"),
                channel_id=_device.get("channel_id"),
                name=_device.get("name"),
                inputs=_device.get("inputs"),
                outputs=_device.get("outputs"),
                parameters=_device.get("parameters"),
                api=self._api,
            )
            for _device in _switch_devices
        ]

    def get_config(self, refresh: bool = False) -> dict:
        """Get the Free@Home Configuration."""
        if self._config is None or refresh:
            self._config = self._api.get_configuration()

        return self._config

    def get_devices_by_function(self, function_id: str) -> list[dict]:
        """Get the list of devices by function."""
        _devices = []
        for _device_key, _device in self.get_config().get("devices").items():
            for _channel_key, _channel in _device.get("channels", {}).items():
                if _channel.get("functionID") == function_id:
                    _name = _channel.get("displayName")
                    if _name == "Ⓐ" or _name is None:
                        _name = _device.get("displayName")

                    _devices.append(
                        {
                            "device_id": _device_key,
                            "channel_id": _channel_key,
                            "name": _name,
                            "function_id": _channel.get("functionID"),
                            "floor_name": self.get_floor_name(
                                floor_serial_id=_channel.get(
                                    "floor", _device.get("floor")
                                )
                            ),
                            "room_name": self.get_room_name(
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

    def get_floor_name(self, floor_serial_id: str) -> str:
        """Get the floor name from the configuration."""
        _default_room = {"name": "unknown", "rooms": {}}
        return self.floors.get(floor_serial_id, _default_room).get("name")

    def get_room_name(self, floor_serial_id: str, room_serial_id: str) -> str:
        """Get the room name from the configuration."""
        _default_room = {"name": "unknown", "rooms": {}}
        return (
            self.floors.get(floor_serial_id, _default_room)
            .get("rooms")
            .get(room_serial_id)
            .get("name", "unknown")
        )


if __name__ == "__main__":
    pass
