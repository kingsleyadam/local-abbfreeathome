"""ABB-Free@Home Device class."""

from typing import Any

from .api import FreeAtHomeApi
from .bin.function import Function
from .bin.interface import Interface
from .channels.base import Base
from .const import FUNCTION_CHANNEL_MAPPING, FUNCTION_VIRTUAL_CHANNEL_MAPPING
from .floorplan import Floorplan


class Device:
    """Represents a Free@Home device with all its attributes."""

    def __init__(
        self,
        device_serial: str,
        device_id: str,
        display_name: str,
        api: FreeAtHomeApi,
        interface: Interface | None = None,
        unresponsive: bool = False,
        unresponsive_counter: int = 0,
        defect: bool = False,
        floor: str | None = None,
        room: str | None = None,
        floor_name: str | None = None,
        room_name: str | None = None,
        device_reboots: str | None = None,
        native_id: str | None = None,
        parameters: dict[str, dict[str, Any]] | None = None,
        channels_data: dict[str, dict] | None = None,
    ) -> None:
        """Initialize the Device class."""
        self._device_serial = device_serial
        self._device_id = device_id
        self._display_name = display_name
        self._interface = interface if interface is not None else Interface.UNDEFINED
        self._unresponsive = unresponsive
        self._unresponsive_counter = unresponsive_counter
        self._defect = defect
        self._floor = floor
        self._room = room
        self._floor_name = floor_name
        self._room_name = room_name
        self._device_reboots = device_reboots
        self._native_id = native_id
        self._parameters = parameters or {}
        self._channels_data = channels_data or {}
        self._channels: dict[str, Base] = {}

        # Expose api as public attribute
        self.api: FreeAtHomeApi = api

    @property
    def device_serial(self) -> str:
        """Return the device serial."""
        return self._device_serial

    @property
    def device_id(self) -> str:
        """Return the device ID."""
        return self._device_id

    @property
    def display_name(self) -> str:
        """Return the device display name."""
        return self._display_name

    @property
    def interface(self) -> Interface:
        """Return the device interface."""
        return self._interface

    @property
    def unresponsive(self) -> bool:
        """Return True if the device is unresponsive."""
        return self._unresponsive

    @property
    def unresponsive_counter(self) -> int:
        """Return the unresponsive counter."""
        return self._unresponsive_counter

    @property
    def defect(self) -> bool:
        """Return True if the device is defective."""
        return self._defect

    @property
    def floor(self) -> str | None:
        """Return the device floor."""
        return self._floor

    @property
    def room(self) -> str | None:
        """Return the device room."""
        return self._room

    @property
    def floor_name(self) -> str | None:
        """Return the device floor name."""
        return self._floor_name

    @property
    def room_name(self) -> str | None:
        """Return the device room name."""
        return self._room_name

    @property
    def device_reboots(self) -> str | None:
        """Return the device reboot count."""
        return self._device_reboots

    @property
    def native_id(self) -> str | None:
        """Return the device native ID."""
        return self._native_id

    @property
    def parameters(self) -> dict[str, dict[str, Any]]:
        """Return the device parameters."""
        return self._parameters

    @property
    def channels_data(self) -> dict[str, dict]:
        """Return the device channels data."""
        return self._channels_data

    @property
    def channels(self) -> dict[str, Base]:
        """Return the device channels."""
        return self._channels

    @property
    def is_virtual(self) -> bool:
        """Return True if this is a virtual device."""
        return self._interface == Interface.VIRTUAL_DEVICE

    @property
    def is_multi_device(self) -> bool:
        """Return True if this is a multi-device."""
        return (
            self._floor is None
            and self._room is None
            and len(self._channels.keys()) > 1
        )

    def clear_channels(self):
        """Clear channels from the device."""
        self._channels.clear()

    def load_channels(self, floorplan: Floorplan):
        """Load the channels object."""
        # Select appropriate mapping based on virtual status
        _function_channel_mapping = (
            FUNCTION_VIRTUAL_CHANNEL_MAPPING
            if self.is_virtual
            else FUNCTION_CHANNEL_MAPPING
        )

        # Create channels dictionary
        self.clear_channels()
        for channel_id, channel_data in self._channels_data.items():
            # Determine channel class based on function ID
            _function_id = channel_data.get("functionID")
            if not _function_id:
                continue

            try:
                _function = Function(int(_function_id, 16))
            except (ValueError, KeyError):
                continue

            _channel_class = _function_channel_mapping.get(_function)
            if not _channel_class:
                continue

            # Create the Channel object
            _channel_name = channel_data.get("displayName", f"Channel {channel_id}")
            if _channel_name in ["Ⓐ", "ⓑ"] or _channel_name is None:
                _channel_name = self.display_name

            # Get floor and room names
            _channel_floor_name = floorplan.get_floor_name(
                floor_id=channel_data.get("floor")
            )
            _channel_room_name = floorplan.get_room_name(
                floor_id=channel_data.get("floor"), room_id=channel_data.get("room")
            )

            _channel = _channel_class(
                device=self,
                channel_id=channel_id,
                channel_name=_channel_name,
                inputs=channel_data.get("inputs", {}),
                outputs=channel_data.get("outputs", {}),
                parameters=channel_data.get("parameters", {}),
                floor_name=_channel_floor_name or self.floor_name,
                room_name=_channel_room_name or self.room_name,
            )

            # Assign channel to channel cache
            self._channels[channel_id] = _channel

        # Return the channels dictionary
        return self._channels

    def __repr__(self) -> str:
        """Return a string representation of the device."""
        return (
            f"Device(device_serial='{self.device_serial}', "
            f"display_name='{self.display_name}', "
            f"interface='{self.interface.value}', "
            f"unresponsive={self.unresponsive})"
        )
