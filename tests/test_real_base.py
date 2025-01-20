"""Test class to test the RealBase device."""

from unittest.mock import MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.real_base import RealBase


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return MagicMock(spec=FreeAtHomeApi)


@pytest.fixture
def real_base_instance(mock_api):
    """Set up the real_base instance for testing the RealBase device."""
    inputs = {
        "idp0000": {"pairingID": 1, "value": "0"},
        "idp0001": {"pairingID": 2, "value": "0"},
        "idp0002": {"pairingID": 3, "value": "0"},
        "idp0003": {"pairingID": 4, "value": "1"},
        "idp0004": {"pairingID": 6, "value": "0"},
    }
    outputs = {
        "odp0000": {"pairingID": 256, "value": "0"},
        "odp0001": {"pairingID": 257, "value": "0"},
    }
    parameters = {}

    return RealBase(
        device_id="ABB7F500E17A",
        device_name="Device Name",
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
        floor_name="Ground Floor",
        room_name="Study",
    )


def test_initialization(real_base_instance):
    """Test the initialization of the real_base class."""
    assert real_base_instance.device_id == "ABB7F500E17A"
    assert real_base_instance.device_name == "Device Name"
    assert real_base_instance.channel_id == "ch0003"
    assert real_base_instance.channel_name == "Channel Name"
    assert real_base_instance.floor_name == "Ground Floor"
    assert real_base_instance.room_name == "Study"


def test_update_device(real_base_instance):
    """Test when input-datapoint is provided."""

    real_base_instance.update_device("AL_SWITCH_ON_OFF/idp0000", "1")
