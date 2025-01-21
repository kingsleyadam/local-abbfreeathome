"""Test class to test the Base device."""

from unittest.mock import MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.pairing import Pairing
from src.abbfreeathome.devices.base import Base
from src.abbfreeathome.exceptions import InvalidDeviceChannelPairing


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return MagicMock(spec=FreeAtHomeApi)


@pytest.fixture
def base_instance(mock_api):
    """Set up the base instance for testing the Base device."""
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

    return Base(
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


def test_initialization(base_instance):
    """Test the initialization of the base class."""
    assert base_instance.device_id == "ABB7F500E17A"
    assert base_instance.device_name == "Device Name"
    assert base_instance.channel_id == "ch0003"
    assert base_instance.channel_name == "Channel Name"
    assert base_instance.floor_name == "Ground Floor"
    assert base_instance.room_name == "Study"


def test_get_input_by_pairing(base_instance):
    """Test the get_input_pairing function."""
    input_id, value = base_instance.get_input_by_pairing(Pairing.AL_SWITCH_ON_OFF)
    assert input_id == "idp0000"
    assert value == "0"

    with pytest.raises(InvalidDeviceChannelPairing):
        base_instance.get_input_by_pairing(Pairing.AL_HSV)


def test_get_output_by_pairing(base_instance):
    """Test the get_output_pairing function."""
    output_id, value = base_instance.get_output_by_pairing(Pairing.AL_INFO_ON_OFF)
    assert output_id == "odp0000"
    assert value == "0"

    with pytest.raises(InvalidDeviceChannelPairing):
        base_instance.get_output_by_pairing(Pairing.AL_HSV)


def test_register_callback(base_instance):
    """Test register a callback."""
    callback = MagicMock()
    base_instance.register_callback(callback)
    assert callback in base_instance._callbacks


def test_remove_callback(base_instance):
    """Test removing a callback."""
    callback = MagicMock()
    base_instance.register_callback(callback)
    base_instance.remove_callback(callback)
    assert callback not in base_instance._callbacks


def test_update_device(base_instance):
    """Test when input-datapoint is provided."""

    base_instance.update_device("AL_SWITCH_ON_OFF/idp0000", "1")
