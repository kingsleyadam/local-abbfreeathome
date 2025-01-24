"""Test class to test the VirtualBase device."""

from unittest.mock import MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi

# from src.abbfreeathome.bin.pairing import Pairing
from src.abbfreeathome.devices.virtual.virtual_base import VirtualBase

# from src.abbfreeathome.exceptions import InvalidDeviceChannelPairing


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return MagicMock(spec=FreeAtHomeApi)


@pytest.fixture
def base_instance(mock_api):
    """Set up the base instance for testing the Base device."""
    inputs = {
        "idp0000": {"pairingID": 1, "value": ""},
        "idp0001": {"pairingID": 2, "value": ""},
        "idp0002": {"pairingID": 3, "value": ""},
        "idp0003": {"pairingID": 4, "value": ""},
        "idp0004": {"pairingID": 6, "value": ""},
    }
    outputs = {
        "odp0000": {"pairingID": 256, "value": "0"},
        "odp0001": {"pairingID": 257, "value": "0"},
    }
    parameters = {}

    return VirtualBase(
        device_id="60004F56EA24",
        device_name="Device Name",
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
        floor_name="Ground Floor",
        room_name="Study",
    )


def test_initialization(base_instance):
    """Test the initialization of the base class."""
    assert base_instance.device_id == "60004F56EA24"
    assert base_instance.device_name == "Device Name"
    assert base_instance.channel_id == "ch0000"
    assert base_instance.channel_name == "Channel Name"
    assert base_instance.floor_name == "Ground Floor"
    assert base_instance.room_name == "Study"


def test_update_device(base_instance):
    """Test when output-datapoint is provided."""

    base_instance.update_device("AL_INFO_ON_OFF/odp0000", "1")
