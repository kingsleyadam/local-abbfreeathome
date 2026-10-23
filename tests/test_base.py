"""Test class to test the Base channel."""

from unittest.mock import MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.pairing import Pairing
from src.abbfreeathome.bin.parameter import Parameter
from src.abbfreeathome.channels.base import Base
from src.abbfreeathome.channels.switch_sensor import SwitchSensor
from src.abbfreeathome.channels.virtual.virtual_dimming_actuator import (
    VirtualDimmingActuator,
)
from src.abbfreeathome.channels.virtual.virtual_room_temperature_controller import (
    VirtualRoomTemperatureController,
)
from src.abbfreeathome.channels.virtual.virtual_switch_actuator import (
    VirtualSwitchActuator,
)
from src.abbfreeathome.channels.virtual.virtual_trigger import VirtualTrigger
from src.abbfreeathome.device import Device
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
def mock_device():
    """Create a mock device function."""
    return MagicMock(spec=Device)


@pytest.fixture
def base_instance(mock_api, mock_device):
    """Set up the base instance for testing the Base channel."""
    mock_device.device_serial = "ABB7F500E17A"
    mock_device.display_name = "Device Name"
    mock_device.unresponsive = False
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
        device=mock_device,
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        floor_name="Ground Floor",
        room_name="Study",
    )
    instance._callback_attributes = ["test"]
    return instance


def test_initialization(base_instance):
    """Test the initialization of the base class."""
    assert base_instance.device_serial == "ABB7F500E17A"
    assert base_instance.device_name == "Device Name"
    assert not base_instance.unresponsive
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


def test_get_channel_parameter(base_instance):
    """Test the get_channel_parameter function."""
    parameter_id, value = base_instance.get_channel_parameter(
        Parameter.PID_TEMPERATURE_COLOR_PHYSICAL_COOLEST
    )
    assert parameter_id == "par00f5"
    assert value == "6500"

    with pytest.raises(InvalidDeviceChannelParameter):
        base_instance.get_channel_parameter(Parameter.PID_DIMMER_SWITCH_ON_MODE)


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


def test_register_callback_existing_attribute(base_instance):
    """Test registering a callback when the attribute already exists in _callbacks."""
    callback1 = MagicMock()
    callback2 = MagicMock()

    # Register first callback - this creates the set in _callbacks
    base_instance.register_callback(callback_attribute="test", callback=callback1)
    assert callback1 in base_instance._callbacks["test"]

    # Register second callback to same attribute - this hits the branch where
    # callback_attribute is already in self._callbacks (line 147 condition is False)
    base_instance.register_callback(callback_attribute="test", callback=callback2)
    assert callback2 in base_instance._callbacks["test"]
    assert callback1 in base_instance._callbacks["test"]  # First callback still there


def test_remove_callback(base_instance):
    """Test removing a callback."""
    callback = MagicMock()
    base_instance.register_callback(callback_attribute="test", callback=callback)
    base_instance.remove_callback(callback_attribute="test", callback=callback)
    assert callback not in base_instance._callbacks["test"]


def test_remove_callback_empty_set(base_instance):
    """Test removing a callback when the callback set is empty."""
    # Set up _callbacks with empty set for "test" attribute
    base_instance._callbacks["test"] = set()

    callback = MagicMock()

    # This should hit the branch where self._callbacks[callback_attribute] is falsy
    # (empty set) and thus the function exits without doing anything (line 160->exit)
    base_instance.remove_callback(callback_attribute="test", callback=callback)

    # The empty set should remain empty
    assert len(base_instance._callbacks["test"]) == 0


def test_remove_callback_nonexistent_attribute(base_instance):
    """Test removing a callback when the callback attribute doesn't exist."""
    callback = MagicMock()

    # This should hit the KeyError branch when trying to access
    # self._callbacks[callback_attribute] for non-existent key
    with pytest.raises(KeyError):
        base_instance.remove_callback(
            callback_attribute="nonexistent", callback=callback
        )


def test_update_channel(base_instance):
    """Test when input-datapoint is provided."""

    base_instance.update_channel("AL_SWITCH_ON_OFF/idp0000", "1")


@pytest.fixture(
    params=[
        (Base, "outputs"),
        (SwitchSensor, "outputs"),
        (SwitchSensor, "inputs"),
        (VirtualSwitchActuator, "outputs"),
        (VirtualSwitchActuator, "inputs"),
        (VirtualDimmingActuator, "outputs"),
        (VirtualDimmingActuator, "inputs"),
        (VirtualRoomTemperatureController, "outputs"),
        (VirtualRoomTemperatureController, "inputs"),
        (VirtualTrigger, "outputs"),
        (VirtualTrigger, "inputs"),
    ]
)
def multi_attribute_channel(request, mock_device, monkeypatch):
    """Exercise every callback dispatcher with multiple affected attributes."""
    channel_class, direction = request.param
    io_key = "odp0000" if direction == "outputs" else "idp0000"
    datapoints = {io_key: {"pairingID": 9999, "value": "0"}}
    channel = channel_class(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=datapoints if direction == "inputs" else {},
        outputs=datapoints if direction == "outputs" else {},
        parameters={},
    )
    channel._callback_attributes = ["test", "other", "unsubscribed"]
    monkeypatch.setattr(
        channel,
        "_refresh_state_from_datapoint",
        MagicMock(return_value=["test", "other", "test", "unsubscribed"]),
    )
    return channel, io_key, datapoints[io_key]


def test_update_channel_multiple_attributes(multi_attribute_channel):
    """Notify every affected group, invoking shared subscribers only once."""
    channel, io_key, datapoint = multi_attribute_channel
    first_callback = MagicMock()
    second_callback = MagicMock()
    observed_values = []
    shared_callback = MagicMock(
        side_effect=lambda: observed_values.append(datapoint["value"])
    )
    channel.register_callback("test", first_callback)
    channel.register_callback("other", second_callback)
    channel.register_callback("test", shared_callback)
    channel.register_callback("other", shared_callback)

    channel.update_channel(f"device/ch0000/{io_key}", "1")

    first_callback.assert_called_once_with()
    second_callback.assert_called_once_with()
    shared_callback.assert_called_once_with()
    assert observed_values == ["1"]
    channel._refresh_state_from_datapoint.assert_called_once_with(datapoint=datapoint)


@pytest.mark.parametrize(
    ("value", "is_priming", "callback_count"),
    [("0", True, 0), ("1", True, 1), ("0", False, 1)],
)
def test_update_channel_multiple_attributes_priming(
    multi_attribute_channel, value, is_priming, callback_count
):
    """Suppress unchanged priming updates but preserve normal notifications."""
    channel, io_key, datapoint = multi_attribute_channel
    first_callback = MagicMock()
    second_callback = MagicMock()
    channel.register_callback("test", first_callback)
    channel.register_callback("other", second_callback)

    channel.update_channel(f"device/ch0000/{io_key}", value, is_priming=is_priming)

    assert first_callback.call_count == callback_count
    assert second_callback.call_count == callback_count
    assert datapoint["value"] == value
    channel._refresh_state_from_datapoint.assert_called_once_with(datapoint=datapoint)


def test_update_channel_multiple_attributes_without_subscribers(
    multi_attribute_channel,
):
    """Refresh multiple attributes even when no callbacks are registered."""
    channel, io_key, datapoint = multi_attribute_channel

    channel.update_channel(f"device/ch0000/{io_key}", "1")

    assert datapoint["value"] == "1"
    assert not any(channel._callbacks.values())


def test_update_channel_without_affected_attributes(
    multi_attribute_channel,
):
    """An unhandled datapoint must not dispatch any callbacks."""
    channel, io_key, _ = multi_attribute_channel
    channel._refresh_state_from_datapoint.return_value = []
    callback = MagicMock()
    channel.register_callback("test", callback)

    channel.update_channel(f"device/ch0000/{io_key}", "1")

    callback.assert_not_called()


def test_base_refresh_returns_empty_list(base_instance):
    """The base implementation reports no affected attributes."""
    assert base_instance._refresh_state_from_datapoint({}) == []


def test_repr(base_instance):
    """Test the __repr__ method."""
    repr_str = repr(base_instance)
    expected = (
        "Channel(class='Base', "
        "channel_id='ch0003', "
        "channel_name='Channel Name', "
        "room_name='Study')"
    )
    assert repr_str == expected
