"""Test class to test the virtual WindowDoorSensor device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.virtual.virtual_window_door_sensor import (
    VirtualWindowDoorSensor,
)


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def virtual_window_door_sensor(mock_api):
    """Set up the sensor instance for testing the virtual WindowDoorSensor device."""
    inputs = {}
    outputs = {
        "odp000c": {"pairingID": 53, "value": "0"},
        "odp000d": {"pairingID": 4, "value": "0"},
    }
    parameters = {}

    return VirtualWindowDoorSensor(
        device_id="60002AE2F1BE",
        device_name="Device Name",
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_turn_on(virtual_window_door_sensor):
    """Test to activate the sensor."""
    await virtual_window_door_sensor.turn_on()
    virtual_window_door_sensor._api.set_datapoint.assert_called_with(
        device_id="60002AE2F1BE",
        channel_id="ch0000",
        datapoint="odp000c",
        value="1",
    )
    assert virtual_window_door_sensor.state is True


@pytest.mark.asyncio
async def test_turn_off(virtual_window_door_sensor):
    """Test to deactivate the sensor."""
    await virtual_window_door_sensor.turn_off()
    virtual_window_door_sensor._api.set_datapoint.assert_called_with(
        device_id="60002AE2F1BE",
        channel_id="ch0000",
        datapoint="odp000c",
        value="0",
    )
    assert virtual_window_door_sensor.state is False


def test_update_device(virtual_window_door_sensor):
    """Test updating the device state."""

    def test_callback():
        pass

    # Ensure callback is registered to test callback code.
    virtual_window_door_sensor.register_callback(
        callback_attribute="state", callback=test_callback
    )

    virtual_window_door_sensor.update_device("AL_SWITCH_ON_OFF/odp000c", "1")
    assert virtual_window_door_sensor.state is True

    virtual_window_door_sensor.update_device("AL_SWITCH_ON_OFF/odp000c", "0")
    assert virtual_window_door_sensor.state is False

    # Test scenario where websocket sends update not relevant to the state.
    virtual_window_door_sensor.update_device("AL_SWITCH_ON_OFF/odp000d", "1")
    assert virtual_window_door_sensor.state is False
