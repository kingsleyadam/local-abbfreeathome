"""Test class to test the virtual WindSensor device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.virtual.virtual_wind_sensor import VirtualWindSensor


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def virtual_wind_sensor(mock_api):
    """Set up the sensor instance for testing the virtual WindSensor device."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 37, "value": ""},
        "odp0001": {"pairingID": 1025, "value": ""},
        "odp0002": {"pairingID": 4, "value": "0"},
        "odp0003": {"pairingID": 1028, "value": ""},
    }
    parameters = {}

    return VirtualWindSensor(
        device_id="6000A0EA2CF4",
        device_name="Device Name",
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_turn_on(virtual_wind_sensor):
    """Test to activate the sensor."""
    await virtual_wind_sensor.turn_on()
    virtual_wind_sensor._api.set_datapoint.assert_called_with(
        device_id="6000A0EA2CF4",
        channel_id="ch0003",
        datapoint="odp0000",
        value="1",
    )
    assert virtual_wind_sensor.alarm is True


@pytest.mark.asyncio
async def test_turn_off(virtual_wind_sensor):
    """Test to deactivate the sensor."""
    await virtual_wind_sensor.turn_off()
    virtual_wind_sensor._api.set_datapoint.assert_called_with(
        device_id="6000A0EA2CF4",
        channel_id="ch0003",
        datapoint="odp0000",
        value="0",
    )
    assert virtual_wind_sensor.alarm is False


@pytest.mark.asyncio
async def test_set_speed(virtual_wind_sensor):
    """Test to set speed of the sensor."""
    """Greater than 0 is ok"""
    await virtual_wind_sensor.set_speed(5)
    virtual_wind_sensor._api.set_datapoint.assert_called_with(
        device_id="6000A0EA2CF4",
        channel_id="ch0003",
        datapoint="odp0003",
        value="5",
    )
    assert virtual_wind_sensor.speed == 5.0

    """Below 0 is always 0"""
    await virtual_wind_sensor.set_speed(-7.5)
    virtual_wind_sensor._api.set_datapoint.assert_called_with(
        device_id="6000A0EA2CF4",
        channel_id="ch0003",
        datapoint="odp0003",
        value="0",
    )
    assert virtual_wind_sensor.speed == 0.0


@pytest.mark.asyncio
async def test_set_force(virtual_wind_sensor):
    """Test to set force of the sensor."""
    """between 0 and 12 is ok"""
    await virtual_wind_sensor.set_force(5)
    virtual_wind_sensor._api.set_datapoint.assert_called_with(
        device_id="6000A0EA2CF4",
        channel_id="ch0003",
        datapoint="odp0001",
        value="5",
    )
    assert virtual_wind_sensor.force == 5

    """Float values should return integer"""
    await virtual_wind_sensor.set_force(5.5)
    virtual_wind_sensor._api.set_datapoint.assert_called_with(
        device_id="6000A0EA2CF4",
        channel_id="ch0003",
        datapoint="odp0001",
        value="5",
    )
    assert virtual_wind_sensor.force == 5

    """Below 0 is always 0"""
    await virtual_wind_sensor.set_force(-7.5)
    virtual_wind_sensor._api.set_datapoint.assert_called_with(
        device_id="6000A0EA2CF4",
        channel_id="ch0003",
        datapoint="odp0001",
        value="0",
    )
    assert virtual_wind_sensor.force == 0

    """Above 12 is always 12"""
    await virtual_wind_sensor.set_force(15)
    virtual_wind_sensor._api.set_datapoint.assert_called_with(
        device_id="6000A0EA2CF4",
        channel_id="ch0003",
        datapoint="odp0001",
        value="12",
    )
    assert virtual_wind_sensor.force == 12
