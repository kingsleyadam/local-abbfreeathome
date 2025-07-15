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
