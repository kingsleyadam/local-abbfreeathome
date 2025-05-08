"""Test class to test the Base device."""

from unittest.mock import MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.pairing import Pairing
from src.abbfreeathome.bin.parameter import Parameter
from src.abbfreeathome.devices.base import Base
from src.abbfreeathome.exceptions import (
    InvalidDeviceChannelPairing,
    InvalidDeviceChannelParameter,
    UnknownCallbackAttributeException,
)


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
    parameters = {
        "par00f5": "6500",
        "par00f6": "2700",
    }

    instance = Base(
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
    instance._callback_attributes = ["test"]
    return instance


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


def test_get_device_parameter(base_instance):
    """Test the get_device_parameter function."""
    parameter_id, value = base_instance.get_device_parameter(
        Parameter.PID_TEMPERATURE_COLOR_PHYSICAL_COOLEST
    )
    assert parameter_id == "par00f5"
    assert value == "6500"

    with pytest.raises(InvalidDeviceChannelParameter):
        base_instance.get_device_parameter(Parameter.PID_DIMMER_SWITCH_ON_MODE)


def test_register_callback(base_instance):
    """Test register a callback."""
    callback = MagicMock()
    base_instance.register_callback(callback_attribute="test", callback=callback)
    assert callback in base_instance._callbacks["test"]
    with pytest.raises(UnknownCallbackAttributeException) as excinfo:
        base_instance.register_callback(
            callback_attribute="not_there", callback=callback
        )
    assert str(excinfo.value) == (
        "Tried to register the callback-atrribute: "
        "not_there"
        ", but only the callback-attributes '"
        "test"
        "' are known."
    )


def test_remove_callback(base_instance):
    """Test removing a callback."""
    callback = MagicMock()
    base_instance.register_callback(callback_attribute="test", callback=callback)
    base_instance.remove_callback(callback_attribute="test", callback=callback)
    assert callback not in base_instance._callbacks["test"]


def test_update_device(base_instance):
    """Test when input-datapoint is provided."""

    base_instance.update_device("AL_SWITCH_ON_OFF/idp0000", "1")
