"""Test class to test the virtual TemperatureSensor device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.virtual.virtual_temperature_sensor import (
    VirtualTemperatureSensor,
)


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def virtual_temperature_sensor(mock_api):
    """Set up the sensor instance for testing the virtual TemperatureSensor device."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 38, "value": ""},
        "odp0001": {"pairingID": 1024, "value": ""},
        "odp0002": {"pairingID": 4, "value": "0"},
    }
    parameters = {}

    return VirtualTemperatureSensor(
        device_id="6000A0EA2CF4",
        device_name="Device Name",
        channel_id="ch0002",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_turn_on(virtual_temperature_sensor):
    """Test to activate the sensor."""
    await virtual_temperature_sensor.turn_on()
    virtual_temperature_sensor._api.set_datapoint.assert_called_with(
        device_id="6000A0EA2CF4",
        channel_id="ch0002",
        datapoint="odp0000",
        value="1",
    )
    assert virtual_temperature_sensor.alarm is True


@pytest.mark.asyncio
async def test_turn_off(virtual_temperature_sensor):
    """Test to deactivate the sensor."""
    await virtual_temperature_sensor.turn_off()
    virtual_temperature_sensor._api.set_datapoint.assert_called_with(
        device_id="6000A0EA2CF4",
        channel_id="ch0002",
        datapoint="odp0000",
        value="0",
    )
    assert virtual_temperature_sensor.alarm is False


@pytest.mark.asyncio
async def test_set_temperature(virtual_temperature_sensor):
    """Test to set temperature of the sensor."""
    await virtual_temperature_sensor.set_temperature(-15.6)
    virtual_temperature_sensor._api.set_datapoint.assert_called_with(
        device_id="6000A0EA2CF4",
        channel_id="ch0002",
        datapoint="odp0001",
        value="-15.6",
    )
    assert virtual_temperature_sensor.temperature == -15.6
