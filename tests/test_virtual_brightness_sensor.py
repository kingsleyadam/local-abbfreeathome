"""Test class to test the virtual BrightnessSensor channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.virtual.virtual_brightness_sensor import (
    VirtualBrightnessSensor,
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
def virtual_brightness_sensor(mock_api, mock_device):
    """Set up the sensor instance for testing the virtual BrightnessSensor channel."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 1026, "value": ""},
        "odp0001": {"pairingID": 1027, "value": ""},
        "odp0002": {"pairingID": 4, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "6000A0EA2CF4"

    mock_device.api = mock_api
    return VirtualBrightnessSensor(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_turn_on(virtual_brightness_sensor):
    """Test to activate the sensor."""
    await virtual_brightness_sensor.turn_on()
    virtual_brightness_sensor.device.api.set_datapoint.assert_called_with(
        device_serial="6000A0EA2CF4",
        channel_id="ch0000",
        datapoint="odp0000",
        value="1",
    )
    assert virtual_brightness_sensor.alarm is True


@pytest.mark.asyncio
async def test_turn_off(virtual_brightness_sensor):
    """Test to deactivate the sensor."""
    await virtual_brightness_sensor.turn_off()
    virtual_brightness_sensor.device.api.set_datapoint.assert_called_with(
        device_serial="6000A0EA2CF4",
        channel_id="ch0000",
        datapoint="odp0000",
        value="0",
    )
    assert virtual_brightness_sensor.alarm is False


@pytest.mark.asyncio
async def test_set_brightness(virtual_brightness_sensor):
    """Test to set brightness of the sensor."""
    """Values greather 0 should always work"""
    await virtual_brightness_sensor.set_brightness(25)
    virtual_brightness_sensor.device.api.set_datapoint.assert_called_with(
        device_serial="6000A0EA2CF4",
        channel_id="ch0000",
        datapoint="odp0001",
        value="25",
    )
    assert virtual_brightness_sensor.brightness == 25

    """Float values should return integer"""
    await virtual_brightness_sensor.set_brightness(13.7)
    virtual_brightness_sensor.device.api.set_datapoint.assert_called_with(
        device_serial="6000A0EA2CF4",
        channel_id="ch0000",
        datapoint="odp0001",
        value="13",
    )
    assert virtual_brightness_sensor.brightness == 13

    """Negative values should return 0"""
    await virtual_brightness_sensor.set_brightness(-3.4)
    virtual_brightness_sensor.device.api.set_datapoint.assert_called_with(
        device_serial="6000A0EA2CF4",
        channel_id="ch0000",
        datapoint="odp0001",
        value="0",
    )
    assert virtual_brightness_sensor.brightness == 0
