"""Test class to test the virtual SwitchActuator channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.virtual.virtual_switch_actuator import (
    VirtualSwitchActuator,
)
from src.abbfreeathome.device import Device


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def mock_device():
    """Create a mock device function."""
    return MagicMock(spec=Device)


@pytest.fixture
def virtual_switch_actuator(mock_api, mock_device):
    """Set up the switch instance for testing the virtual SwitchActuator channel."""
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

    mock_device.device_serial = "60004F56EA24"

    mock_device.api = mock_api
    return VirtualSwitchActuator(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_initial_state(virtual_switch_actuator):
    """Test the intial state of the virtual switch."""
    assert virtual_switch_actuator.state is False


@pytest.mark.asyncio
async def test_turn_on(virtual_switch_actuator):
    """Test to turning on of the switch."""
    await virtual_switch_actuator.turn_on()
    assert virtual_switch_actuator.state is True
    virtual_switch_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="60004F56EA24",
        channel_id="ch0000",
        datapoint="odp0000",
        value="1",
    )


@pytest.mark.asyncio
async def test_turn_off(virtual_switch_actuator):
    """Test to turning off of the switch."""
    await virtual_switch_actuator.turn_off()
    assert virtual_switch_actuator.state is False
    virtual_switch_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="60004F56EA24",
        channel_id="ch0000",
        datapoint="odp0000",
        value="0",
    )


@pytest.mark.asyncio
async def test_refresh_state(virtual_switch_actuator):
    """Test refreshing the state of the switch."""
    virtual_switch_actuator.device.api.get_datapoint.return_value = ["1"]
    await virtual_switch_actuator.refresh_state()
    assert virtual_switch_actuator.state is True
    virtual_switch_actuator.device.api.get_datapoint.assert_called_with(
        device_serial="60004F56EA24",
        channel_id="ch0000",
        datapoint="odp0000",
    )


def test_update_channel(virtual_switch_actuator):
    """Test updating the channel state."""

    def test_callback():
        pass

    # Ensure callback is registered to test callback code.
    virtual_switch_actuator.register_callback(
        callback_attribute="state", callback=test_callback
    )
    virtual_switch_actuator.register_callback(
        callback_attribute="requested_state", callback=test_callback
    )

    virtual_switch_actuator.update_channel("AL_SWITCH_ON_OFF/odp0000", "1")
    assert virtual_switch_actuator.state is True

    virtual_switch_actuator.update_channel("AL_SWITCH_ON_OFF/odp0000", "0")
    assert virtual_switch_actuator.state is False

    virtual_switch_actuator.update_channel("AL_SWITCH_ON_OFF/idp0000", "1")
    assert virtual_switch_actuator.requested_state is True

    virtual_switch_actuator.update_channel("AL_SWITCH_ON_OFF/idp0000", "0")
    assert virtual_switch_actuator.requested_state is False

    # Test scenario where websocket sends update not relevant to the state.
    virtual_switch_actuator.update_channel("AL_SWITCH_ON_OFF/idp0001", "1")
    assert virtual_switch_actuator.state is False


def test_update_channel_priming_suppresses_noop_callback(virtual_switch_actuator):
    """
    During priming an unchanged datapoint updates cache but fires no callback.

    A changed datapoint during priming still fires, so genuinely-changed state
    is surfaced after a reconnect (#239 suppress-no-ops).
    """
    callback = MagicMock()
    virtual_switch_actuator.register_callback(
        callback_attribute="state", callback=callback
    )

    # Seed a known state outside priming.
    virtual_switch_actuator.update_channel("AL_SWITCH_ON_OFF/odp0000", "1")
    assert virtual_switch_actuator.state is True
    callback.reset_mock()

    # No-op replay during priming -> suppressed.
    virtual_switch_actuator.update_channel(
        "AL_SWITCH_ON_OFF/odp0000", "1", is_priming=True
    )
    assert virtual_switch_actuator.state is True
    callback.assert_not_called()

    # Changed value during priming -> still fires.
    virtual_switch_actuator.update_channel(
        "AL_SWITCH_ON_OFF/odp0000", "0", is_priming=True
    )
    assert virtual_switch_actuator.state is False
    callback.assert_called_once()


@pytest.mark.parametrize("value", [None, "", "invalid", "2", "01", " 1", 0, 1, True])
@pytest.mark.parametrize(
    ("datapoint", "attribute"),
    [("idp0000", "requested_state"), ("odp0000", "state")],
)
def test_invalid_switching_value(
    virtual_switch_actuator, value, datapoint, attribute, caplog
):
    """Expose malformed switching telegrams as unknown and recover on valid data."""
    callback = MagicMock()
    virtual_switch_actuator.register_callback(attribute, callback)
    virtual_switch_actuator.update_channel(datapoint, "1")
    callback.reset_mock()

    virtual_switch_actuator.update_channel(datapoint, value)

    assert getattr(virtual_switch_actuator, attribute) is None
    callback.assert_called_once_with()
    if value is not None and value != "":
        assert "Invalid switching value" in caplog.text

    virtual_switch_actuator.update_channel(datapoint, "0")
    assert getattr(virtual_switch_actuator, attribute) is False


@pytest.mark.parametrize("value", [None, "", "invalid", "2"])
def test_invalid_scene_request(virtual_switch_actuator, value):
    """Do not turn malformed scene values into off requests."""
    requested_states = []
    virtual_switch_actuator.register_callback(
        "requested_state",
        lambda: requested_states.append(virtual_switch_actuator.requested_state),
    )

    for scene_value in ("1", value, "0"):
        virtual_switch_actuator.update_scene("odp0000", scene_value)

    assert requested_states == [True, None, False]


@pytest.mark.parametrize("is_priming", [False, True])
def test_update_scene_repeated_request(virtual_switch_actuator, is_priming):
    """Test every scene emits a request, including repeats and event-only users."""
    callback = MagicMock()
    virtual_switch_actuator.register_callback("requested_state", callback)

    for value in ("1", "1", "0", "0"):
        virtual_switch_actuator.update_scene(
            "60004F56EA24/ch0000/odp0000", value, is_priming=is_priming
        )
        assert virtual_switch_actuator.state is (value == "1")
        assert virtual_switch_actuator.requested_state is (value == "1")

    assert callback.call_count == 4
    virtual_switch_actuator.device.api.set_datapoint.assert_not_called()


def test_update_scene_without_callbacks(virtual_switch_actuator):
    """Test scene state is updated when no subscribers are registered."""
    virtual_switch_actuator.update_scene("60004F56EA24/ch0000/odp0000", "1")

    assert virtual_switch_actuator.state is True
    assert virtual_switch_actuator.requested_state is True


@pytest.mark.parametrize("datapoint", ["odp0001", "odp9999"])
def test_update_scene_unrelated_output(virtual_switch_actuator, datapoint):
    """Test unrelated and unknown scene outputs do not emit switch requests."""
    callback = MagicMock()
    virtual_switch_actuator.register_callback("requested_state", callback)

    virtual_switch_actuator.update_scene(f"60004F56EA24/ch0000/{datapoint}", "1")

    assert virtual_switch_actuator.state is False
    assert virtual_switch_actuator.requested_state is None
    callback.assert_not_called()


def test_update_channel_output_feedback_does_not_request(virtual_switch_actuator):
    """Test output feedback cannot retrigger an event-driven switch automation."""
    callback = MagicMock()
    virtual_switch_actuator.register_callback("requested_state", callback)

    virtual_switch_actuator.update_scene("60004F56EA24/ch0000/odp0000", "1")
    callback.assert_called_once_with()
    callback.reset_mock()

    virtual_switch_actuator.update_channel("60004F56EA24/ch0000/odp0000", "1")
    virtual_switch_actuator.update_channel("60004F56EA24/ch0000/odp0000", "0")

    assert virtual_switch_actuator.state is False
    callback.assert_not_called()
