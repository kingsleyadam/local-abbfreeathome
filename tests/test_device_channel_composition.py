"""Test Device/Channel composition pattern."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.function import Function
from src.abbfreeathome.bin.interface import Interface
from src.abbfreeathome.channels.dimming_actuator import DimmingActuator
from src.abbfreeathome.channels.switch_actuator import SwitchActuator
from src.abbfreeathome.device import Device


@pytest.fixture
def mock_api():
    """Create a mock API object."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def mock_device():
    """Create a mock device function."""
    return MagicMock(spec=Device)


@pytest.fixture
def test_device_with_channels(mock_api, mock_device):
    """Create a test device with mock channel data."""
    channels_data = {
        "ch0000": {
            "displayName": "Test Switch",
            "functionID": hex(Function.FID_SWITCH_ACTUATOR.value)[2:].upper().zfill(4),
            "inputs": {"idp0000": {"pairingID": 1, "value": "0"}},
            "outputs": {"odp0000": {"pairingID": 256, "value": "0"}},
            "parameters": {},
        },
        "ch0001": {
            "displayName": "Test Dimmer",
            "functionID": hex(Function.FID_DIMMING_ACTUATOR.value)[2:].upper().zfill(4),
            "inputs": {
                "idp0000": {"pairingID": 1, "value": "0"},
                "idp0001": {"pairingID": 2, "value": "0"},
            },
            "outputs": {
                "odp0000": {"pairingID": 256, "value": "0"},
                "odp0001": {"pairingID": 257, "value": "0"},
            },
            "parameters": {},
        },
    }

    return Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        interface=Interface.WIRED_BUS,
        unresponsive=False,
        unresponsive_counter=0,
        defect=False,
        floor="00000000-0000-0000-0000-000000000000",
        room="00000000-0000-0000-0000-000000000001",
        floor_name="Ground Floor",
        room_name="Living Room",
        device_reboots="0",
        native_id=None,
        parameters={},
        channels_data=channels_data,
        api=mock_api,
    )


def test_device_channels_property_returns_channel_objects(test_device_with_channels):
    """Test that device.channels returns Channel objects."""
    # Since channels property now returns None until load_channels is called
    assert test_device_with_channels.channels == {}


def test_device_load_channels_returns_channel_objects(
    test_device_with_channels, mock_floorplan
):
    """Test that device.load_channels() returns Channel objects."""
    channels = test_device_with_channels.load_channels(mock_floorplan)

    assert len(channels) == 2
    assert "ch0000" in channels
    assert "ch0001" in channels

    # Verify channel types
    assert isinstance(channels["ch0000"], SwitchActuator)
    assert isinstance(channels["ch0001"], DimmingActuator)


def test_channel_has_device_reference(test_device_with_channels, mock_floorplan):
    """Test that each Channel has a reference to its parent Device."""
    test_device_with_channels.load_channels(mock_floorplan)
    channels = test_device_with_channels.channels

    for channel in channels.values():
        assert channel.device is test_device_with_channels
        assert channel.device.display_name == "Test Device"


def test_channels_are_cached(test_device_with_channels, mock_floorplan):
    """Test that channels are cached and same objects returned."""
    channels1 = test_device_with_channels.load_channels(mock_floorplan)
    channels2 = test_device_with_channels.channels

    # Should return the same dictionary instance
    assert channels1 is channels2

    # Individual channel objects should be the same
    if channels1:
        first_channel_id = list(channels1.keys())[0]
        assert channels1[first_channel_id] is channels2[first_channel_id]


def test_device_with_empty_channels_data(mock_api, mock_device, mock_floorplan):
    """Test that device with empty channels_data returns empty channels dict."""
    device = Device(
        device_serial="ABB7F500E17B",
        device_id="910D",
        display_name="Device With Empty Channels",
        channels_data={},  # Empty channels data
        api=mock_api,
    )

    channels = device.load_channels(mock_floorplan)
    assert len(channels) == 0
    assert isinstance(channels, dict)
    assert device.channels == {}


def test_channel_properties_correct(test_device_with_channels, mock_floorplan):
    """Test that channel properties are correctly set."""
    test_device_with_channels.load_channels(mock_floorplan)
    channels = test_device_with_channels.channels
    switch_channel = channels["ch0000"]

    assert switch_channel.channel_id == "ch0000"
    assert switch_channel.channel_name == "Test Switch"
    assert switch_channel.device_name == "Test Device"
    assert switch_channel.device_serial == "ABB7F500E17A"
    assert switch_channel.floor_name == "Ground Floor"
    assert switch_channel.room_name == "Living Room"


def test_invalid_channel_function_skipped(mock_api, mock_device, mock_floorplan):
    """Test that channels with invalid function IDs are skipped."""
    channels_data = {
        "ch0000": {
            "displayName": "Valid Switch",
            "functionID": hex(Function.FID_SWITCH_ACTUATOR.value)[2:].upper().zfill(4),
            "inputs": {},
            "outputs": {},
            "parameters": {},
        },
        "ch0001": {
            "displayName": "Invalid Function",
            "functionID": "FFFF",  # Invalid function ID
            "inputs": {},
            "outputs": {},
            "parameters": {},
        },
        "ch0002": {
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
        channels_data=channels_data,
        api=mock_api,
    )

    channels = device.load_channels(mock_floorplan)

    # Only the valid channel should be created
    assert len(channels) == 1
    assert "ch0000" in channels
    assert isinstance(channels["ch0000"], SwitchActuator)


def test_channels_data_property_unchanged(test_device_with_channels):
    """Test that channels_data property still returns raw data."""
    channels_data = test_device_with_channels.channels_data

    assert len(channels_data) == 2
    assert "ch0000" in channels_data
    assert "ch0001" in channels_data

    # Should be raw dict data, not Channel objects
    assert isinstance(channels_data["ch0000"], dict)
    assert channels_data["ch0000"]["displayName"] == "Test Switch"
