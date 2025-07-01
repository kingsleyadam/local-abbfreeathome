"""Test class to test the virtual TemperatureSensor channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.virtual.virtual_temperature_sensor import (
    VirtualTemperatureSensor,
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
def virtual_temperature_sensor(mock_api, mock_device):
    """Set up the sensor instance for testing the virtual TemperatureSensor channel."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 38, "value": ""},
        "odp0001": {"pairingID": 1024, "value": ""},
        "odp0002": {"pairingID": 4, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "6000A0EA2CF4"

    mock_device.api = mock_api
    return VirtualTemperatureSensor(
        device=mock_device,
        channel_id="ch0002",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_turn_on(virtual_temperature_sensor):
    """Test to activate the sensor."""
    await virtual_temperature_sensor.turn_on()
    virtual_temperature_sensor.device.api.set_datapoint.assert_called_with(
        device_serial="6000A0EA2CF4",
        channel_id="ch0002",
        datapoint="odp0000",
        value="1",
    )
    assert virtual_temperature_sensor.alarm is True


@pytest.mark.asyncio
async def test_turn_off(virtual_temperature_sensor):
    """Test to deactivate the sensor."""
    await virtual_temperature_sensor.turn_off()
    virtual_temperature_sensor.device.api.set_datapoint.assert_called_with(
        device_serial="6000A0EA2CF4",
        channel_id="ch0002",
        datapoint="odp0000",
        value="0",
    )
    assert virtual_temperature_sensor.alarm is False


@pytest.mark.asyncio
async def test_set_temperature(virtual_temperature_sensor):
    """Test to set temperature of the sensor."""
    await virtual_temperature_sensor.set_temperature(-15.6)
    virtual_temperature_sensor.device.api.set_datapoint.assert_called_with(
        device_serial="6000A0EA2CF4",
        channel_id="ch0002",
        datapoint="odp0001",
        value="-15.6",
    )
    assert virtual_temperature_sensor.temperature == -15.6
