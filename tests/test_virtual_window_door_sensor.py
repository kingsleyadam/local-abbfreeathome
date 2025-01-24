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
async def test_set_on(virtual_window_door_sensor):
    """Test to activate the sensor."""
    await virtual_window_door_sensor.set_on()
    virtual_window_door_sensor._api.set_datapoint.assert_called_with(
        device_id="60002AE2F1BE",
        channel_id="ch0000",
        datapoint="odp000c",
        value="1",
    )
    assert virtual_window_door_sensor.state is True


@pytest.mark.asyncio
async def test_set_off(virtual_window_door_sensor):
    """Test to deactivate the sensor."""
    await virtual_window_door_sensor.set_off()
    virtual_window_door_sensor._api.set_datapoint.assert_called_with(
        device_id="60002AE2F1BE",
        channel_id="ch0000",
        datapoint="odp000c",
        value="0",
    )
    assert virtual_window_door_sensor.state is False
