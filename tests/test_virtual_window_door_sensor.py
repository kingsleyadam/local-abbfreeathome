"""Test class to test the virtual WindowDoorSensor channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.virtual.virtual_window_door_sensor import (
    VirtualWindowDoorSensor,
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
def virtual_window_door_sensor(mock_api, mock_device):
    """Set up the sensor instance for testing the virtual WindowDoorSensor channel."""
    inputs = {}
    outputs = {
        "odp000c": {"pairingID": 53, "value": "0"},
        "odp000d": {"pairingID": 4, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "60002AE2F1BE"

    mock_device.api = mock_api
    return VirtualWindowDoorSensor(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_turn_on(virtual_window_door_sensor):
    """Test to activate the sensor."""
    await virtual_window_door_sensor.turn_on()
    virtual_window_door_sensor.device.api.set_datapoint.assert_called_with(
        device_serial="60002AE2F1BE",
        channel_id="ch0000",
        datapoint="odp000c",
        value="1",
    )
    assert virtual_window_door_sensor.state is True


@pytest.mark.asyncio
async def test_turn_off(virtual_window_door_sensor):
    """Test to deactivate the sensor."""
    await virtual_window_door_sensor.turn_off()
    virtual_window_door_sensor.device.api.set_datapoint.assert_called_with(
        device_serial="60002AE2F1BE",
        channel_id="ch0000",
        datapoint="odp000c",
        value="0",
    )
    assert virtual_window_door_sensor.state is False


def test_update_channel(virtual_window_door_sensor):
    """Test updating the channel state."""

    def test_callback():
        pass

    # Ensure callback is registered to test callback code.
    virtual_window_door_sensor.register_callback(
        callback_attribute="state", callback=test_callback
    )

    virtual_window_door_sensor.update_channel("AL_SWITCH_ON_OFF/odp000c", "1")
    assert virtual_window_door_sensor.state is True

    virtual_window_door_sensor.update_channel("AL_SWITCH_ON_OFF/odp000c", "0")
    assert virtual_window_door_sensor.state is False

    # Test scenario where websocket sends update not relevant to the state.
    virtual_window_door_sensor.update_channel("AL_SWITCH_ON_OFF/odp000d", "1")
    assert virtual_window_door_sensor.state is False
