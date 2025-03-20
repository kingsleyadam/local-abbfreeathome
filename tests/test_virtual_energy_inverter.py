"""Test class to test the virtual EnergyInverter device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.virtual.virtual_energy_inverter import (
    VirtualEnergyInverter,
)


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def virtual_energy_inverter(mock_api):
    """Set up the sensor instance for testing the virtual EnergyInverter device."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 1190, "value": ""},
        "odp0001": {"pairingID": 1191, "value": ""},
        "odp0002": {"pairingID": 1221, "value": ""},
        "odp0003": {"pairingID": 1222, "value": ""},
        "odp0004": {"pairingID": 1224, "value": ""},
    }
    parameters = {}

    return VirtualEnergyInverter(
        device_id="6000702DC087",
        device_name="Device Name",
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_set_current_power(virtual_energy_inverter):
    """Test to set current_power of the sensor."""
    await virtual_energy_inverter.set_current_power(435.7)
    virtual_energy_inverter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0003",
        datapoint="odp0002",
        value="435.7",
    )
    assert virtual_energy_inverter.current_power == 435.7


@pytest.mark.asyncio
async def test_set_imported_today(virtual_energy_inverter):
    """Test to set imported_today of the sensor."""
    """Values greater 0 should always work"""
    await virtual_energy_inverter.set_imported_today(25)
    virtual_energy_inverter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0003",
        datapoint="odp0003",
        value="25",
    )
    assert virtual_energy_inverter.imported_today == 25

    """Float values should return integer"""
    await virtual_energy_inverter.set_imported_today(13.7)
    virtual_energy_inverter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0003",
        datapoint="odp0003",
        value="13",
    )
    assert virtual_energy_inverter.imported_today == 13

    """Negative values should return 0"""
    await virtual_energy_inverter.set_imported_today(-3.4)
    virtual_energy_inverter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0003",
        datapoint="odp0003",
        value="0",
    )
    assert virtual_energy_inverter.imported_today == 0


@pytest.mark.asyncio
async def test_set_imported_total(virtual_energy_inverter):
    """Test to set imported_total of the sensor."""
    """Values greater 0 should always work"""
    await virtual_energy_inverter.set_imported_total(25)
    virtual_energy_inverter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0003",
        datapoint="odp0004",
        value="25",
    )
    assert virtual_energy_inverter.imported_total == 25

    """Float values should return integer"""
    await virtual_energy_inverter.set_imported_total(13.7)
    virtual_energy_inverter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0003",
        datapoint="odp0004",
        value="13",
    )
    assert virtual_energy_inverter.imported_total == 13

    """Negative values should return 0"""
    await virtual_energy_inverter.set_imported_total(-3.4)
    virtual_energy_inverter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0003",
        datapoint="odp0004",
        value="0",
    )
    assert virtual_energy_inverter.imported_total == 0
