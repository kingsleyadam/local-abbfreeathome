"""Test class to test the Base channel."""

from unittest.mock import AsyncMock, MagicMock

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
from src.abbfreeathome.const import (
    FUNCTION_CHANNEL_MAPPING,
    FUNCTION_VIRTUAL_CHANNEL_MAPPING,
)
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
        "Unknown callback-attribute 'not_there'; known callback-attributes: 'test'."
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
    """Test input updates are ignored unless the channel opts in."""
    base_instance._refresh_state_from_datapoint = MagicMock(return_value=[])

    base_instance.update_channel("AL_SWITCH_ON_OFF/idp0000", "1")
    assert base_instance._inputs["idp0000"]["value"] == "0"
    base_instance._refresh_state_from_datapoint.assert_not_called()

    base_instance._handle_input_updates = True
    base_instance.update_channel("AL_SWITCH_ON_OFF/idp0000", "1")
    assert base_instance._inputs["idp0000"]["value"] == "1"
    base_instance._refresh_state_from_datapoint.assert_called_once_with(
        datapoint={"pairingID": 1, "value": "1"}
    )


@pytest.mark.asyncio
async def test_input_refresh_pairings(mock_api, mock_device, monkeypatch):
    """Test only listed inputs are loaded and refreshed; missing ones are skipped."""
    monkeypatch.setattr(
        Base,
        "_input_refresh_pairings",
        [Pairing.AL_SWITCH_ON_OFF, Pairing.AL_HSV],
    )
    refreshed = []
    monkeypatch.setattr(
        Base,
        "_refresh_state_from_datapoint",
        lambda self, datapoint: refreshed.append(dict(datapoint)) or [],
    )
    mock_device.device_serial = "ABB7F500E17A"
    mock_device.api = mock_api
    mock_api.get_datapoint = AsyncMock(return_value=["1"])
    channel = Base(
        device=mock_device,
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs={
            "idp0000": {"pairingID": 1, "value": "0"},
            "idp0001": {"pairingID": 2, "value": "0"},
        },
        outputs={},
        parameters={},
    )
    assert refreshed == [{"pairingID": 1, "value": "0"}]

    refreshed.clear()
    await channel.refresh_state()

    mock_api.get_datapoint.assert_awaited_once_with(
        device_serial="ABB7F500E17A", channel_id="ch0003", datapoint="idp0000"
    )
    assert refreshed == [{"pairingID": 1, "value": "1"}]
    assert channel._inputs["idp0000"]["value"] == "1"


@pytest.mark.asyncio
async def test_refresh_state_notifies_callbacks(mock_api, mock_device, monkeypatch):
    """Cache refreshed values, then notify once, except for command attributes."""
    monkeypatch.setattr(Base, "_state_refresh_pairings", [Pairing.AL_INFO_ON_OFF])
    monkeypatch.setattr(Base, "_input_refresh_pairings", [Pairing.AL_SWITCH_ON_OFF])
    monkeypatch.setattr(
        Base,
        "_refresh_state_from_datapoint",
        lambda self, datapoint: (
            ["output", "command"]
            if datapoint["pairingID"] == Pairing.AL_INFO_ON_OFF.value
            else ["input", "command"]
        ),
    )
    mock_device.device_serial = "ABB7F500E17A"
    mock_device.api = mock_api
    mock_api.get_datapoint = AsyncMock(side_effect=[["1"], ["2"]])
    channel = Base(
        device=mock_device,
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs={"idp0000": {"pairingID": 1, "value": "0"}},
        outputs={"odp0000": {"pairingID": 256, "value": "0"}},
        parameters={},
    )
    channel._callback_attributes = ["output", "input", "command"]
    channel._command_callback_attributes = ["command"]
    callbacks = {attribute: MagicMock() for attribute in channel._callback_attributes}
    for attribute, callback in callbacks.items():
        channel.register_callback(attribute, callback)
    observed_values = []
    shared_callback = MagicMock(
        side_effect=lambda: observed_values.append(
            (channel._outputs["odp0000"]["value"], channel._inputs["idp0000"]["value"])
        )
    )
    channel.register_callback("output", shared_callback)
    channel.register_callback("input", shared_callback)

    await channel.refresh_state()

    assert channel._outputs["odp0000"]["value"] == "1"
    assert channel._inputs["idp0000"]["value"] == "2"
    callbacks["output"].assert_called_once_with()
    callbacks["input"].assert_called_once_with()
    callbacks["command"].assert_not_called()
    shared_callback.assert_called_once_with()
    assert observed_values == [("1", "2")]


@pytest.mark.asyncio
async def test_refresh_state_partial_failure(mock_api, mock_device, monkeypatch):
    """Notify the values already read when a later request fails."""
    monkeypatch.setattr(Base, "_state_refresh_pairings", [Pairing.AL_INFO_ON_OFF])
    monkeypatch.setattr(Base, "_input_refresh_pairings", [Pairing.AL_SWITCH_ON_OFF])
    monkeypatch.setattr(
        Base,
        "_refresh_state_from_datapoint",
        lambda self, datapoint: (
            ["output"]
            if datapoint["pairingID"] == Pairing.AL_INFO_ON_OFF.value
            else ["input"]
        ),
    )
    mock_device.device_serial = "ABB7F500E17A"
    mock_device.api = mock_api
    mock_api.get_datapoint = AsyncMock(side_effect=[["1"], ConnectionError])
    channel = Base(
        device=mock_device,
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs={"idp0000": {"pairingID": 1, "value": "0"}},
        outputs={"odp0000": {"pairingID": 256, "value": "0"}},
        parameters={},
    )
    channel._callback_attributes = ["output", "input"]
    output_callback = MagicMock()
    # A failing subscriber must not replace the request's exception.
    failing_callback = MagicMock(side_effect=RuntimeError("subscriber bug"))
    input_callback = MagicMock()
    channel.register_callback("output", output_callback)
    channel.register_callback("output", failing_callback)
    channel.register_callback("input", input_callback)

    with pytest.raises(ConnectionError):
        await channel.refresh_state()

    assert channel._outputs["odp0000"]["value"] == "1"
    output_callback.assert_called_once_with()
    failing_callback.assert_called_once_with()
    input_callback.assert_not_called()


@pytest.mark.parametrize(
    "channel_class",
    sorted(
        {
            *FUNCTION_CHANNEL_MAPPING.values(),
            *FUNCTION_VIRTUAL_CHANNEL_MAPPING.values(),
        },
        key=lambda channel_class: channel_class.__name__,
    ),
    ids=lambda channel_class: channel_class.__name__,
)
def test_command_callback_attributes_are_callback_attributes(channel_class):
    """Every command attribute must also be a subscribable callback attribute."""
    assert set(channel_class._command_callback_attributes) <= set(
        channel_class._callback_attributes
    )
    # The same holds for the attribute refresh mapping, whose pairings must
    # also be refreshed by refresh_state() without attributes.
    assert set(channel_class._attribute_refresh_pairings) <= set(
        channel_class._callback_attributes
    )
    for _pairings in channel_class._attribute_refresh_pairings.values():
        assert set(_pairings) <= {
            *channel_class._state_refresh_pairings,
            *channel_class._input_refresh_pairings,
        }


@pytest.fixture
def attribute_refresh_channel(mock_api, mock_device, monkeypatch):
    """Return a Base channel with two outputs and one input to refresh."""
    monkeypatch.setattr(
        Base,
        "_state_refresh_pairings",
        [Pairing.AL_INFO_ON_OFF, Pairing.AL_INFO_ACTUAL_DIMMING_VALUE],
    )
    monkeypatch.setattr(Base, "_input_refresh_pairings", [Pairing.AL_SWITCH_ON_OFF])
    monkeypatch.setattr(
        Base,
        "_attribute_refresh_pairings",
        {
            "state": [Pairing.AL_INFO_ON_OFF, Pairing.AL_SWITCH_ON_OFF],
            "brightness": [Pairing.AL_INFO_ACTUAL_DIMMING_VALUE],
        },
    )
    attributes_by_pairing = {
        Pairing.AL_INFO_ON_OFF.value: ["state"],
        Pairing.AL_INFO_ACTUAL_DIMMING_VALUE.value: ["brightness"],
        Pairing.AL_SWITCH_ON_OFF.value: ["state"],
    }
    monkeypatch.setattr(
        Base,
        "_refresh_state_from_datapoint",
        lambda self, datapoint: attributes_by_pairing.get(datapoint["pairingID"], []),
    )
    mock_device.device_serial = "ABB7F500E17A"
    mock_device.api = mock_api
    mock_api.get_datapoint = AsyncMock(return_value=["1"])
    channel = Base(
        device=mock_device,
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs={"idp0000": {"pairingID": 1, "value": "0"}},
        outputs={
            "odp0000": {"pairingID": 256, "value": "0"},
            "odp0001": {"pairingID": 272, "value": "0"},
        },
        parameters={},
    )
    channel._callback_attributes = ["state", "brightness", "unmapped"]
    return channel


@pytest.mark.asyncio
async def test_refresh_state_attributes(attribute_refresh_channel, mock_api):
    """Read only the pairings of the requested attributes and notify those."""
    callbacks = {"state": MagicMock(), "brightness": MagicMock()}
    for attribute, callback in callbacks.items():
        attribute_refresh_channel.register_callback(attribute, callback)

    await attribute_refresh_channel.refresh_state(attributes=["state"])

    assert [
        _call.kwargs["datapoint"] for _call in mock_api.get_datapoint.await_args_list
    ] == ["odp0000", "idp0000"]
    callbacks["state"].assert_called_once_with()
    callbacks["brightness"].assert_not_called()


@pytest.mark.parametrize(
    "attributes",
    [None, [], ["brightness", "unmapped"]],
    ids=["all", "empty", "unmapped"],
)
@pytest.mark.asyncio
async def test_refresh_state_attributes_fallback(
    attribute_refresh_channel, mock_api, attributes
):
    """Read every pairing by default, for no attributes, or for unmapped ones."""
    await attribute_refresh_channel.refresh_state(attributes=attributes)

    assert [
        _call.kwargs["datapoint"] for _call in mock_api.get_datapoint.await_args_list
    ] == ["odp0000", "odp0001", "idp0000"]


@pytest.mark.parametrize(
    "attributes",
    [["unknown"], ["unmapped", "unknown"], ["unknown", "unmapped"]],
    ids=["unknown", "unmapped-first", "unknown-first"],
)
@pytest.mark.asyncio
async def test_refresh_state_unknown_attribute(
    attribute_refresh_channel, mock_api, attributes
):
    """Reject an unknown attribute before sending any request, in any order."""
    with pytest.raises(UnknownCallbackAttributeException):
        await attribute_refresh_channel.refresh_state(attributes=attributes)

    mock_api.get_datapoint.assert_not_awaited()


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


def test_notify_callbacks_isolates_failing_callback(base_instance, caplog):
    """A failing subscriber is logged and does not block other subscribers."""
    failing_callback = MagicMock(side_effect=RuntimeError("subscriber bug"))
    callback = MagicMock()
    base_instance.register_callback("test", failing_callback)
    base_instance.register_callback("test", callback)

    base_instance._notify_callbacks(["test"])

    failing_callback.assert_called_once_with()
    callback.assert_called_once_with()
    assert "Error in callback for ABB7F500E17A/ch0003" in caplog.text
    assert "subscriber bug" in caplog.text


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
