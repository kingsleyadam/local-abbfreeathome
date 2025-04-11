"""Test class to test the virtual EnergyTwoWayMeter device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.virtual.virtual_energy_two_way_meter import (
    VirtualEnergyTwoWayMeter,
)


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def virtual_energy_two_way_meter(mock_api):
    """Set up the sensor instance for testing the virtual EnergyTwoWayMeter device."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 1221, "value": ""},
        "odp0001": {"pairingID": 1229, "value": ""},
        "odp0002": {"pairingID": 1222, "value": ""},
        "odp0003": {"pairingID": 1223, "value": ""},
        "odp0004": {"pairingID": 1224, "value": ""},
        "odp0005": {"pairingID": 1225, "value": ""},
        "odp0006": {"pairingID": 1234, "value": ""},
        "odp0007": {"pairingID": 1235, "value": ""},
    }
    parameters = {}

    return VirtualEnergyTwoWayMeter(
        device_id="6000702DC087",
        device_name="Device Name",
        channel_id="ch0001",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_set_current_power(virtual_energy_two_way_meter):
    """Test to set battery_power of the sensor."""
    await virtual_energy_two_way_meter.set_current_power(435.7)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0000",
        value="435.7",
    )
    assert virtual_energy_two_way_meter.current_power == 435.7


@pytest.mark.asyncio
async def test_set_imported_today(virtual_energy_two_way_meter):
    """Test to set imported_today of the sensor."""
    """Values greater 0 should always work"""
    await virtual_energy_two_way_meter.set_imported_today(25)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0002",
        value="25",
    )
    assert virtual_energy_two_way_meter.imported_today == 25

    """Float values should return integer"""
    await virtual_energy_two_way_meter.set_imported_today(13.7)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0002",
        value="13",
    )
    assert virtual_energy_two_way_meter.imported_today == 13

    """Negative values should return 0"""
    await virtual_energy_two_way_meter.set_imported_today(-3.4)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0002",
        value="0",
    )
    assert virtual_energy_two_way_meter.imported_today == 0


@pytest.mark.asyncio
async def test_set_exported_today(virtual_energy_two_way_meter):
    """Test to set exported_today of the sensor."""
    """Values greater 0 should always work"""
    await virtual_energy_two_way_meter.set_exported_today(25)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0003",
        value="25",
    )
    assert virtual_energy_two_way_meter.exported_today == 25

    """Float values should return integer"""
    await virtual_energy_two_way_meter.set_exported_today(13.7)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0003",
        value="13",
    )
    assert virtual_energy_two_way_meter.exported_today == 13

    """Negative values should return 0"""
    await virtual_energy_two_way_meter.set_exported_today(-3.4)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0003",
        value="0",
    )
    assert virtual_energy_two_way_meter.exported_today == 0


@pytest.mark.asyncio
async def test_set_imported_total(virtual_energy_two_way_meter):
    """Test to set imported_total of the sensor."""
    """Values greater 0 should always work"""
    await virtual_energy_two_way_meter.set_imported_total(25)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0004",
        value="25",
    )
    assert virtual_energy_two_way_meter.imported_total == 25

    """Float values should return integer"""
    await virtual_energy_two_way_meter.set_imported_total(13.7)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0004",
        value="13",
    )
    assert virtual_energy_two_way_meter.imported_total == 13

    """Negative values should return 0"""
    await virtual_energy_two_way_meter.set_imported_total(-3.4)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0004",
        value="0",
    )
    assert virtual_energy_two_way_meter.imported_total == 0


@pytest.mark.asyncio
async def test_set_exported_total(virtual_energy_two_way_meter):
    """Test to set exported_total of the sensor."""
    """Values greater 0 should always work"""
    await virtual_energy_two_way_meter.set_exported_total(25)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0005",
        value="25",
    )
    assert virtual_energy_two_way_meter.exported_total == 25

    """Float values should return integer"""
    await virtual_energy_two_way_meter.set_exported_total(13.7)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0005",
        value="13",
    )
    assert virtual_energy_two_way_meter.exported_total == 13

    """Negative values should return 0"""
    await virtual_energy_two_way_meter.set_exported_total(-3.4)
    virtual_energy_two_way_meter._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0001",
        datapoint="odp0005",
        value="0",
    )
    assert virtual_energy_two_way_meter.exported_total == 0
