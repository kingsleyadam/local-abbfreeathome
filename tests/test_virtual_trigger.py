"""Test class to test the virtual Trigger channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.virtual.virtual_trigger import VirtualTrigger
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
def virtual_trigger(mock_api, mock_device):
    """Set up the trigger instance for testing the virtual Trigger channel."""
    inputs = {
        "idp0001": {"pairingID": 2, "value": ""},
        "idp0003": {"pairingID": 4, "value": ""},
    }
    outputs = {}
    parameters = {}

    mock_device.device_serial = "60001DFE59A4"
    mock_device.api = mock_api
    return VirtualTrigger(
        device=mock_device,
        channel_id="ch0000",
        channel_name="TRG Test Pushbutton",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_press(virtual_trigger):
    """Test to press the virtual trigger."""
    await virtual_trigger.press()
    virtual_trigger.device.api.set_datapoint.assert_called_with(
        device_serial="60001DFE59A4",
        channel_id="ch0000",
        datapoint="idp0001",
        value="1",
    )


def test_update_channel(virtual_trigger):
    """Test updating the channel state from websocket."""

    def test_callback():
        pass

    virtual_trigger.register_callback(
        callback_attribute="triggered", callback=test_callback
    )

    virtual_trigger.update_channel("AL_TIMED_START_STOP/idp0001", "1")
    assert virtual_trigger.triggered is True

    virtual_trigger.update_channel("AL_TIMED_START_STOP/idp0001", "0")
    assert virtual_trigger.triggered is False

    # Test scenario where websocket sends update not relevant to the state.
    virtual_trigger.update_channel("AL_SCENE_CONTROL/idp0003", "1")
    assert virtual_trigger.triggered is False

    # Test scenario where websocket sends update for unknown datapoint.
    virtual_trigger.update_channel("AL_UNKNOWN/odp0099", "1")
    assert virtual_trigger.triggered is False


def test_update_channel_output(mock_api, mock_device):
    """Test updating the channel state from an output datapoint."""
    inputs = {
        "idp0001": {"pairingID": 2, "value": ""},
    }
    outputs = {
        "odp0000": {"pairingID": 2, "value": ""},
    }
    mock_device.device_serial = "60001DFE59A4"
    mock_device.api = mock_api
    trigger = VirtualTrigger(
        device=mock_device,
        channel_id="ch0000",
        channel_name="TRG Test Pushbutton",
        inputs=inputs,
        outputs=outputs,
        parameters={},
    )

    def test_callback():
        pass

    trigger.register_callback(callback_attribute="triggered", callback=test_callback)

    trigger.update_channel("AL_TIMED_START_STOP/odp0000", "1")
    assert trigger.triggered is True
