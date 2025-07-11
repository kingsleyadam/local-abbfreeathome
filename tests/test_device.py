"""Test code for the Device class."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.function import Function
from src.abbfreeathome.bin.interface import Interface
from src.abbfreeathome.channels.switch_actuator import SwitchActuator
from src.abbfreeathome.channels.virtual.virtual_switch_actuator import (
    VirtualSwitchActuator,
)
from src.abbfreeathome.device import Device


@pytest.fixture
def mock_api():
    """Create a mock API for testing."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def mock_device():
    """Create a mock device for testing."""
    return MagicMock(spec=Device)


def test_device_initialization_minimal(mock_api, mock_device):
    """Test Device initialization with minimal parameters."""
    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
    )

    assert device.device_serial == "ABB7F500E17A"
    assert device.device_id == "910C"
    assert device.display_name == "Test Device"
    assert device.interface == Interface.UNDEFINED
    assert device.unresponsive is False
    assert device.unresponsive_counter == 0
    assert device.defect is False
    assert device.floor is None
    assert device.room is None
    assert device.floor_name is None
    assert device.room_name is None
    assert device.device_reboots is None
    assert device.native_id is None
    assert device.parameters == {}
    assert device.channels_data == {}
    assert device.channels == {}
    assert device.is_virtual is False
    assert device.is_multi_device is False


def test_device_initialization_full(mock_api, mock_device):
    """Test Device initialization with all parameters."""
    test_parameters = {"par0001": "value1", "par0002": "value2"}
    test_channels = {
        "ch0000": {"displayName": "Channel 1"},
        "ch0001": {"displayName": "Channel 2"},
    }

    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        interface=Interface.WIRED_BUS,
        unresponsive=True,
        unresponsive_counter=5,
        defect=True,
        floor="01",
        room="02",
        floor_name="Ground Floor",
        room_name="Living Room",
        device_reboots="10",
        native_id="NATIVE123",
        parameters=test_parameters,
        channels_data=test_channels,
    )

    assert device.device_serial == "ABB7F500E17A"
    assert device.device_id == "910C"
    assert device.display_name == "Test Device"
    assert device.interface == Interface.WIRED_BUS
    assert device.unresponsive is True
    assert device.unresponsive_counter == 5
    assert device.defect is True
    assert device.floor == "01"
    assert device.room == "02"
    assert device.floor_name == "Ground Floor"
    assert device.room_name == "Living Room"
    assert device.device_reboots == "10"
    assert device.native_id == "NATIVE123"
    assert device.parameters == test_parameters
    assert device.channels_data == test_channels
    assert device.is_virtual is False
    assert device.is_multi_device is False


def test_device_virtual_detection(mock_api, mock_device):
    """Test virtual device detection based on device serial."""
    # Test virtual device (starts with 6000)
    virtual_device = Device(
        device_serial="60005D808C54",
        device_id="0161",
        display_name="Virtual Device",
        api=mock_api,
        interface=Interface.VIRTUAL_DEVICE,
    )
    assert virtual_device.is_virtual is True

    # Test non-virtual device (doesn't start with 6000)
    physical_device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Physical Device",
        api=mock_api,
    )
    assert physical_device.is_virtual is False


def test_device_interface_enum(mock_api, mock_device):
    """Test device interface with different Interface enum values."""
    test_cases = [
        (Interface.WIRED_BUS, "TP"),
        (Interface.WIRELESS_RF, "RF"),
        (Interface.HUE, "hue"),
        (Interface.SONOS, "sonos"),
        (Interface.VIRTUAL_DEVICE, "VD"),
        (Interface.SMOKEALARM, "smokealarm"),
        (Interface.UNDEFINED, None),
    ]

    for interface_enum, expected_value in test_cases:
        device = Device(
            device_serial="TEST",
            device_id="TEST",
            display_name="Test Device",
            api=mock_api,
            interface=interface_enum,
        )
        assert device.interface == interface_enum
        assert device.interface.value == expected_value


def test_device_parameters_default(mock_api, mock_device):
    """Test device parameters default to empty dict when None."""
    device = Device(
        device_serial="TEST",
        device_id="TEST",
        display_name="Test Device",
        api=mock_api,
        parameters=None,
    )
    assert device.parameters == {}


def test_device_channels_default(mock_api, mock_device):
    """Test device channels default to empty dict when None."""
    device = Device(
        device_serial="TEST",
        device_id="TEST",
        display_name="Test Device",
        api=mock_api,
        channels_data=None,
    )
    assert device.channels_data == {}


def test_device_repr(mock_api, mock_device):
    """Test device string representation."""
    # Test with interface enum
    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        interface=Interface.WIRED_BUS,
        unresponsive=True,
    )

    repr_str = repr(device)
    assert "device_serial='ABB7F500E17A'" in repr_str
    assert "display_name='Test Device'" in repr_str
    assert "interface='TP'" in repr_str
    assert "unresponsive=True" in repr_str


def test_device_repr_no_interface(mock_api, mock_device):
    """Test device string representation with no interface."""
    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        interface=None,
        unresponsive=False,
    )

    repr_str = repr(device)
    assert "device_serial='ABB7F500E17A'" in repr_str
    assert "display_name='Test Device'" in repr_str
    assert "interface='None'" in repr_str
    assert "unresponsive=False" in repr_str


def test_device_repr_undefined_interface(mock_api, mock_device):
    """Test device string representation with undefined interface."""
    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        interface=Interface.UNDEFINED,
        unresponsive=False,
    )

    repr_str = repr(device)
    assert "device_serial='ABB7F500E17A'" in repr_str
    assert "display_name='Test Device'" in repr_str
    assert "interface='None'" in repr_str
    assert "unresponsive=False" in repr_str


def test_device_all_properties(mock_api, mock_device):
    """Test all device properties are accessible."""
    test_parameters = {"par0001": "value1"}
    test_channels = {"ch0000": {"displayName": "Channel 1"}}

    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        interface=Interface.HUE,
        unresponsive=True,
        unresponsive_counter=3,
        defect=False,
        floor="02",
        room="05",
        floor_name="First Floor",
        room_name="Bedroom",
        device_reboots="15",
        native_id="NATIVE456",
        parameters=test_parameters,
        channels_data=test_channels,
    )

    # Test all properties are accessible and return correct values
    assert device.device_serial == "ABB7F500E17A"
    assert device.device_id == "910C"
    assert device.display_name == "Test Device"
    assert device.interface == Interface.HUE
    assert device.unresponsive is True
    assert device.unresponsive_counter == 3
    assert device.defect is False
    assert device.floor == "02"
    assert device.room == "05"
    assert device.floor_name == "First Floor"
    assert device.room_name == "Bedroom"
    assert device.device_reboots == "15"
    assert device.native_id == "NATIVE456"
    assert device.parameters is test_parameters
    assert device.channels_data is test_channels
    assert device.is_virtual is False


def test_device_empty_strings(mock_api, mock_device):
    """Test device with empty string values."""
    device = Device(
        device_serial="",
        device_id="",
        display_name="",
        api=mock_api,
        floor="",
        room="",
        device_reboots="",
        native_id="",
    )

    assert device.device_serial == ""
    assert device.device_id == ""
    assert device.display_name == ""
    assert device.floor == ""
    assert device.room == ""
    assert device.device_reboots == ""
    assert device.native_id == ""
    assert device.is_virtual is False  # Empty string doesn't start with "6000"


def test_device_interface_conversion(mock_api, mock_device):
    """Test interface conversion for different interface values."""
    # Test that the device properly handles Interface enum values
    interfaces_to_test = [
        Interface.UNDEFINED,
        Interface.WIRED_BUS,
        Interface.WIRELESS_RF,
        Interface.HUE,
        Interface.SONOS,
        Interface.VIRTUAL_DEVICE,
        Interface.SMOKEALARM,
    ]

    for interface in interfaces_to_test:
        device = Device(
            device_serial="TEST",
            device_id="TEST",
            display_name="Test Device",
            api=mock_api,
            interface=interface,
        )
        assert device.interface == interface

        # Test repr handles the interface correctly
        repr_str = repr(device)
        expected_value = interface.value if interface.value is not None else "None"
        assert f"interface='{expected_value}'" in repr_str


def test_device_floor_room_names_properties(mock_api, mock_device):
    """Test floor_name and room_name properties specifically."""
    # Test with both floor and room names
    device_with_names = Device(
        device_serial="TEST",
        device_id="TEST",
        display_name="Test Device",
        api=mock_api,
        floor="01",
        room="02",
        floor_name="Ground Floor",
        room_name="Living Room",
    )

    assert device_with_names.floor == "01"
    assert device_with_names.room == "02"
    assert device_with_names.floor_name == "Ground Floor"
    assert device_with_names.room_name == "Living Room"

    # Test with None values
    device_no_names = Device(
        device_serial="TEST",
        device_id="TEST",
        display_name="Test Device",
        api=mock_api,
        floor=None,
        room=None,
        floor_name=None,
        room_name=None,
    )

    assert device_no_names.floor is None
    assert device_no_names.room is None
    assert device_no_names.floor_name is None
    assert device_no_names.room_name is None


def test_device_load_channels_empty(mock_floorplan):
    """Test loading channels with empty channels_data."""
    mock_api = AsyncMock(spec=FreeAtHomeApi)

    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        channels_data={},
    )

    channels = device.load_channels(mock_floorplan)

    assert channels == {}
    assert device.channels == {}


def test_device_load_channels_with_valid_data(mock_floorplan):
    """Test loading channels with valid channel data."""
    mock_api = AsyncMock(spec=FreeAtHomeApi)

    channels_data = {
        "ch0000": {
            "displayName": "Test Switch",
            "floor": "01",
            "room": "18",
            "functionID": hex(Function.FID_SWITCH_ACTUATOR.value)[2:].upper().zfill(4),
            "inputs": {"idp0000": {"pairingID": 1, "value": "0"}},
            "outputs": {"odp0000": {"pairingID": 256, "value": "0"}},
            "parameters": {},
        }
    }

    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        channels_data=channels_data,
    )

    channels = device.load_channels(mock_floorplan)

    assert len(channels) == 1
    assert "ch0000" in channels
    assert isinstance(channels["ch0000"], SwitchActuator)
    assert device.channels == channels

    # Verify that the channel has the correct floor and room names from floorplan
    channel = channels["ch0000"]
    assert channel.floor_name == "Ground Floor"
    assert channel.room_name == "Living Room"


def test_device_load_channels_with_existing_floor_room_names(mock_floorplan):
    """Test loading channels when floor_name and room_name are already provided."""
    mock_api = AsyncMock(spec=FreeAtHomeApi)

    channels_data = {
        "ch0000": {
            "displayName": "Test Switch",
            "functionID": hex(Function.FID_SWITCH_ACTUATOR.value)[2:].upper().zfill(4),
            "inputs": {"idp0000": {"pairingID": 1, "value": "0"}},
            "outputs": {"odp0000": {"pairingID": 256, "value": "0"}},
            "parameters": {},
        }
    }

    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        channels_data=channels_data,
        floor="01",
        room="02",
        floor_name="Existing Floor",
        room_name="Existing Room",
    )

    channels = device.load_channels(mock_floorplan)

    assert len(channels) == 1
    assert "ch0000" in channels
    channel = channels["ch0000"]
    assert channel.floor_name == "Existing Floor"
    assert channel.room_name == "Existing Room"

    # The existing floor/room names should be used, not looked up from floorplan


def test_device_load_channels_invalid_function_id(mock_floorplan):
    """Test loading channels with invalid function IDs."""
    mock_api = AsyncMock(spec=FreeAtHomeApi)

    channels_data = {
        "ch0000": {
            "displayName": "Invalid Function",
            "functionID": "FFFF",  # Invalid function ID
            "inputs": {},
            "outputs": {},
            "parameters": {},
        },
        "ch0001": {
            "displayName": "No Function ID",
            # Missing functionID
            "inputs": {},
            "outputs": {},
            "parameters": {},
        },
    }

    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        channels_data=channels_data,
    )

    channels = device.load_channels(mock_floorplan)

    # Both channels should be skipped due to invalid/missing function IDs
    assert len(channels) == 0
    assert device.channels == {}


def test_device_load_channels_virtual_device(mock_floorplan):
    """Test loading channels for virtual device uses virtual mapping."""
    mock_api = AsyncMock(spec=FreeAtHomeApi)

    channels_data = {
        "ch0000": {
            "displayName": "Virtual Switch",
            "functionID": hex(Function.FID_SWITCH_ACTUATOR.value)[2:].upper().zfill(4),
            "inputs": {"idp0000": {"pairingID": 1, "value": "0"}},
            "outputs": {"odp0000": {"pairingID": 256, "value": "0"}},
            "parameters": {},
        }
    }

    device = Device(
        device_serial="60005D808C54",  # Virtual device serial
        device_id="0161",
        display_name="Virtual Test Device",
        api=mock_api,
        interface=Interface.VIRTUAL_DEVICE,
        channels_data=channels_data,
    )

    channels = device.load_channels(mock_floorplan)

    assert len(channels) == 1
    assert "ch0000" in channels
    assert isinstance(channels["ch0000"], VirtualSwitchActuator)


def test_device_load_channels_special_channel_names(mock_floorplan):
    """Test loading channels with special channel names (Ⓐ, ⓑ, None)."""
    mock_api = AsyncMock(spec=FreeAtHomeApi)

    channels_data = {
        "ch0000": {
            "displayName": "Ⓐ",  # Special character
            "functionID": hex(Function.FID_SWITCH_ACTUATOR.value)[2:].upper().zfill(4),
            "inputs": {},
            "outputs": {},
            "parameters": {},
        },
        "ch0001": {
            "displayName": "ⓑ",  # Special character
            "functionID": hex(Function.FID_SWITCH_ACTUATOR.value)[2:].upper().zfill(4),
            "inputs": {},
            "outputs": {},
            "parameters": {},
        },
        "ch0002": {
            "displayName": None,  # None name
            "functionID": hex(Function.FID_SWITCH_ACTUATOR.value)[2:].upper().zfill(4),
            "inputs": {},
            "outputs": {},
            "parameters": {},
        },
    }

    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        channels_data=channels_data,
    )

    channels = device.load_channels(mock_floorplan)

    assert len(channels) == 3

    # All channels with special names should use device name
    for channel in channels.values():
        assert channel.channel_name == "Test Device"


def test_device_clear_channels(mock_api, mock_device):
    """Test the clear_channels method."""
    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
    )

    # Set some channels and then clear them
    device._channels = {"ch0000": "some_channel"}
    device.clear_channels()
    assert device._channels == {}


def test_device_load_channels_with_missing_function_id(
    mock_api, mock_device, mock_floorplan
):
    """Test load_channels with channel data missing functionID."""
    channels_data = {
        "ch0000": {
            "displayName": "Test Channel",
            # Missing functionID
        }
    }

    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        channels_data=channels_data,
    )

    device.load_channels(mock_floorplan)
    # Should have empty channels dict since functionID is missing
    assert device.channels == {}


def test_device_load_channels_with_invalid_function_id(
    mock_api, mock_device, mock_floorplan
):
    """Test load_channels with invalid functionID that can't be converted to hex."""
    channels_data = {
        "ch0000": {
            "displayName": "Test Channel",
            "functionID": "invalid_hex",  # Invalid hex value
        }
    }

    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        channels_data=channels_data,
    )

    device.load_channels(mock_floorplan)
    # Should have empty channels dict since functionID is invalid
    assert device.channels == {}


def test_device_load_channels_with_unknown_function(
    mock_api, mock_device, mock_floorplan
):
    """Test load_channels with functionID that doesn't map to a known channel class."""
    channels_data = {
        "ch0000": {
            "displayName": "Test Channel",
            "functionID": "FFFF",  # Valid hex but unknown function
        }
    }

    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        api=mock_api,
        channels_data=channels_data,
    )

    device.load_channels(mock_floorplan)
    # Should have empty channels dict since function is unknown
    assert device.channels == {}
