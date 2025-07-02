"""Test class to test the virtual RainSensor channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.virtual.virtual_rain_sensor import VirtualRainSensor
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
def virtual_rain_sensor(mock_api, mock_device):
    """Set up the sensor instance for testing the virtual RainSensor channel."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 39, "value": ""},
        "odp0001": {"pairingID": 4, "value": "0"},
        "odp0002": {"pairingID": 1029, "value": ""},
        "odp0003": {"pairingID": 1030, "value": ""},
    }
    parameters = {}

    mock_device.device_serial = "6000A0EA2CF4"

    mock_device.api = mock_api
    return VirtualRainSensor(
        device=mock_device,
        channel_id="ch0001",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_turn_on(virtual_rain_sensor):
    """Test to activate the sensor."""
    await virtual_rain_sensor.turn_on()
    virtual_rain_sensor.device.api.set_datapoint.assert_called_with(
        device_serial="6000A0EA2CF4",
        channel_id="ch0001",
        datapoint="odp0000",
        value="1",
    )
    assert virtual_rain_sensor.alarm is True


@pytest.mark.asyncio
async def test_turn_off(virtual_rain_sensor):
    """Test to deactivate the sensor."""
    await virtual_rain_sensor.turn_off()
    virtual_rain_sensor.device.api.set_datapoint.assert_called_with(
        device_serial="6000A0EA2CF4",
        channel_id="ch0001",
        datapoint="odp0000",
        value="0",
    )
    assert virtual_rain_sensor.alarm is False
