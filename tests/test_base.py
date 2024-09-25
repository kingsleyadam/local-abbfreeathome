"""Test class to test the Base device."""

from unittest.mock import MagicMock

import pytest

from abbfreeathome.api import FreeAtHomeApi
from abbfreeathome.devices.base import Base
from abbfreeathome.exceptions import InvalidDeviceChannelPairingId


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return MagicMock(spec=FreeAtHomeApi)


@pytest.fixture
def base_instance(mock_api):
    """Set up the base instance for testing the Base device."""
    inputs = {
        "input1": {"pairingID": 1, "value": "input_value1"},
        "input2": {"pairingID": 2, "value": "input_value2"},
    }
    outputs = {
        "output1": {"pairingID": 1, "value": "output_value1"},
        "output2": {"pairingID": 2, "value": "output_value2"},
    }
    parameters = {}

    return Base(
        device_id="device123",
        device_name="Device Name",
        channel_id="channel123",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


def test_initialization(base_instance):
    """Test the initialization of the base class."""
    assert base_instance.device_id == "device123"
    assert base_instance.device_name == "Device Name"
    assert base_instance.channel_id == "channel123"
    assert base_instance.channel_name == "Channel Name"


def test_get_input_by_pairing_id(base_instance):
    """Test the get_input_pairing_id function."""
    input_id, value = base_instance.get_input_by_pairing_id(1)
    assert input_id == "input1"
    assert value == "input_value1"

    with pytest.raises(InvalidDeviceChannelPairingId):
        base_instance.get_input_by_pairing_id(99)


def test_get_output_by_pairing_id(base_instance):
    """Test the get_output_pairing_id function."""
    output_id, value = base_instance.get_output_by_pairing_id(1)
    assert output_id == "output1"
    assert value == "output_value1"

    with pytest.raises(InvalidDeviceChannelPairingId):
        base_instance.get_output_by_pairing_id(99)


def test_register_callback(base_instance):
    """Test register a callback."""
    callback = MagicMock()
    base_instance.register_callback(callback)
    assert callback in base_instance._callbacks  # noqa: SLF001


def test_remove_callback(base_instance):
    """Test removing a callback."""
    callback = MagicMock()
    base_instance.register_callback(callback)
    base_instance.remove_callback(callback)
    assert callback not in base_instance._callbacks  # noqa: SLF001
