"""Test code for the Device class."""

from src.abbfreeathome.bin.interface import Interface
from src.abbfreeathome.device import Device


def test_device_initialization_minimal():
    """Test Device initialization with minimal parameters."""
    device = Device(
        device_serial="ABB7F500E17A", device_id="910C", display_name="Test Device"
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
    assert device.channels == {}
    assert device.is_virtual is False


def test_device_initialization_full():
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
        channels=test_channels,
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
    assert device.channels == test_channels
    assert device.is_virtual is False


def test_device_virtual_detection():
    """Test virtual device detection based on device serial."""
    # Test virtual device (starts with 6000)
    virtual_device = Device(
        device_serial="6000F91624D1",
        device_id="0161",
        display_name="Virtual Device",
        interface=Interface.VIRTUAL_DEVICE,
    )
    assert virtual_device.is_virtual is True

    # Test non-virtual device (doesn't start with 6000)
    physical_device = Device(
        device_serial="ABB7F500E17A", device_id="910C", display_name="Physical Device"
    )
    assert physical_device.is_virtual is False


def test_device_interface_enum():
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
            device_serial="TEST123",
            device_id="TEST",
            display_name="Test Device",
            interface=interface_enum,
        )
        assert device.interface == interface_enum
        assert device.interface.value == expected_value


def test_device_parameters_default():
    """Test device parameters default to empty dict when None."""
    device = Device(
        device_serial="TEST123",
        device_id="TEST",
        display_name="Test Device",
        parameters=None,
    )
    assert device.parameters == {}


def test_device_channels_default():
    """Test device channels default to empty dict when None."""
    device = Device(
        device_serial="TEST123",
        device_id="TEST",
        display_name="Test Device",
        channels=None,
    )
    assert device.channels == {}


def test_device_repr():
    """Test device string representation."""
    # Test with interface enum
    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        interface=Interface.WIRED_BUS,
        unresponsive=True,
    )

    repr_str = repr(device)
    assert "device_serial='ABB7F500E17A'" in repr_str
    assert "display_name='Test Device'" in repr_str
    assert "interface='TP'" in repr_str
    assert "unresponsive=True" in repr_str


def test_device_repr_no_interface():
    """Test device string representation with no interface."""
    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        interface=None,
        unresponsive=False,
    )

    repr_str = repr(device)
    assert "device_serial='ABB7F500E17A'" in repr_str
    assert "display_name='Test Device'" in repr_str
    assert "interface='None'" in repr_str
    assert "unresponsive=False" in repr_str


def test_device_repr_undefined_interface():
    """Test device string representation with undefined interface."""
    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        interface=Interface.UNDEFINED,
        unresponsive=False,
    )

    repr_str = repr(device)
    assert "device_serial='ABB7F500E17A'" in repr_str
    assert "display_name='Test Device'" in repr_str
    assert "interface='None'" in repr_str
    assert "unresponsive=False" in repr_str


def test_device_all_properties():
    """Test all device properties are accessible."""
    test_parameters = {"par0001": "value1"}
    test_channels = {"ch0000": {"displayName": "Channel 1"}}

    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
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
        channels=test_channels,
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
    assert device.channels is test_channels
    assert device.is_virtual is False


def test_device_empty_strings():
    """Test device with empty string values."""
    device = Device(
        device_serial="",
        device_id="",
        display_name="",
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


def test_device_interface_conversion():
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
            device_serial="TEST123",
            device_id="TEST",
            display_name="Test Device",
            interface=interface,
        )
        assert device.interface == interface

        # Test repr handles the interface correctly
        repr_str = repr(device)
        expected_value = interface.value if interface.value is not None else "None"
        assert f"interface='{expected_value}'" in repr_str


def test_device_floor_room_names_properties():
    """Test floor_name and room_name properties specifically."""
    # Test with both floor and room names
    device_with_names = Device(
        device_serial="TEST123",
        device_id="TEST",
        display_name="Test Device",
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
        device_serial="TEST456",
        device_id="TEST",
        display_name="Test Device",
        floor=None,
        room=None,
        floor_name=None,
        room_name=None,
    )

    assert device_no_names.floor is None
    assert device_no_names.room is None
    assert device_no_names.floor_name is None
    assert device_no_names.room_name is None
