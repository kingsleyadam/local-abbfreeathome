"""ABB-Free@Home Device class."""

from typing import Any

from .bin.interface import Interface


class Device:
    """Represents a Free@Home device with all its attributes."""

    def __init__(
        self,
        device_serial: str,
        device_id: str,
        display_name: str,
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
        channels: dict[str, dict] | None = None,
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
        self._channels = channels or {}

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
    def parameters(self) -> dict[str, Any]:
        """Return the device parameters."""
        return self._parameters

    @property
    def channels(self) -> dict[str, dict]:
        """Return the device channels."""
        return self._channels

    @property
    def is_virtual(self) -> bool:
        """Return True if this is a virtual device."""
        return self._interface == Interface.VIRTUAL_DEVICE

    def __repr__(self) -> str:
        """Return a string representation of the device."""
        interface_value = self.interface.value if self.interface else None
        return (
            f"Device(device_serial='{self.device_serial}', "
            f"display_name='{self.display_name}', "
            f"interface='{interface_value}', "
            f"unresponsive={self.unresponsive})"
        )
