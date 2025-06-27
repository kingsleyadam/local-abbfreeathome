"""ABB-Free@Home wrapper for interacting with the ABB-free@home API."""

from .api import FreeAtHomeApi
from .bin.function import Function
from .bin.interface import Interface
from .channels.base import Base
from .const import FUNCTION_CHANNEL_MAPPING, FUNCTION_VIRTUAL_CHANNEL_MAPPING


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

        self.api: FreeAtHomeApi = api

        self._interfaces: list[Interface] | None = interfaces
        self._channel_classes: list[type[Base]] | None = channel_classes
        self._include_orphan_channels: bool = include_orphan_channels

    def clear_channels(self):
        """Clear all channels in the channels list."""
        self._channels.clear()

    async def get_config(self, refresh: bool = False) -> dict:
        """Get the Free@Home Configuration."""
        if self._config is None or refresh:
            self._config = await self.api.get_configuration()

        return self._config

    def get_channels(self) -> dict[str, Base]:
        """Get the list of channels."""
        return self._channels

    def get_channels_by_class(self, channel_class: Base) -> list[Base]:
        """Get the list of channels by class."""
        return [
            _channel
            for _channel in self._channels.values()
            if type(_channel) is channel_class
        ]

    async def get_channels_by_function(self, function: Function) -> list[dict]:
        """Get the list of channels by function."""
        _channels = []
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

                    _channels.append(
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
        await self.load_channels()

    async def load_channels(self):
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
                f"{_channel.get('device_id')}/{_channel.get('channel_id')}"
            ] = channel_class(
                device_id=_channel.get("device_id"),
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
