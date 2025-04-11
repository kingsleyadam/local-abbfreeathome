"""Test class to test the virtual EnergyBattery device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.virtual.virtual_energy_battery import (
    VirtualEnergyBattery,
)


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def virtual_energy_battery(mock_api):
    """Set up the sensor instance for testing the virtual EnergyBattery device."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 1197, "value": ""},
        "odp0001": {"pairingID": 1196, "value": ""},
        "odp0002": {"pairingID": 1222, "value": ""},
        "odp0003": {"pairingID": 1223, "value": ""},
        "odp0004": {"pairingID": 1224, "value": ""},
        "odp0005": {"pairingID": 1225, "value": ""},
        "odp0006": {"pairingID": 4, "value": ""},
    }
    parameters = {}

    return VirtualEnergyBattery(
        device_id="6000702DC087",
        device_name="Device Name",
        channel_id="ch0002",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_set_battery_power(virtual_energy_battery):
    """Test to set battery_power of the sensor."""
    await virtual_energy_battery.set_battery_power(435.7)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0000",
        value="435.7",
    )
    assert virtual_energy_battery.battery_power == 435.7


@pytest.mark.asyncio
async def test_set_soc(virtual_energy_battery):
    """Test to set soc of the sensor."""
    """between 0 and 100 is ok"""
    await virtual_energy_battery.set_soc(55)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0001",
        value="55",
    )
    assert virtual_energy_battery.soc == 55

    """Float values should return integer"""
    await virtual_energy_battery.set_soc(5.5)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0001",
        value="5",
    )
    assert virtual_energy_battery.soc == 5

    """Below 0 is always 0"""
    await virtual_energy_battery.set_soc(-7.5)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0001",
        value="0",
    )
    assert virtual_energy_battery.soc == 0

    """Above 100 is always 100"""
    await virtual_energy_battery.set_soc(150)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0001",
        value="100",
    )
    assert virtual_energy_battery.soc == 100


@pytest.mark.asyncio
async def test_set_imported_today(virtual_energy_battery):
    """Test to set imported_today of the sensor."""
    """Values greater 0 should always work"""
    await virtual_energy_battery.set_imported_today(25)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0002",
        value="25",
    )
    assert virtual_energy_battery.imported_today == 25

    """Float values should return integer"""
    await virtual_energy_battery.set_imported_today(13.7)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0002",
        value="13",
    )
    assert virtual_energy_battery.imported_today == 13

    """Negative values should return 0"""
    await virtual_energy_battery.set_imported_today(-3.4)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0002",
        value="0",
    )
    assert virtual_energy_battery.imported_today == 0


@pytest.mark.asyncio
async def test_set_exported_today(virtual_energy_battery):
    """Test to set exported_today of the sensor."""
    """Values greater 0 should always work"""
    await virtual_energy_battery.set_exported_today(25)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0003",
        value="25",
    )
    assert virtual_energy_battery.exported_today == 25

    """Float values should return integer"""
    await virtual_energy_battery.set_exported_today(13.7)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0003",
        value="13",
    )
    assert virtual_energy_battery.exported_today == 13

    """Negative values should return 0"""
    await virtual_energy_battery.set_exported_today(-3.4)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0003",
        value="0",
    )
    assert virtual_energy_battery.exported_today == 0


@pytest.mark.asyncio
async def test_set_imported_total(virtual_energy_battery):
    """Test to set imported_total of the sensor."""
    """Values greater 0 should always work"""
    await virtual_energy_battery.set_imported_total(25)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0004",
        value="25",
    )
    assert virtual_energy_battery.imported_total == 25

    """Float values should return integer"""
    await virtual_energy_battery.set_imported_total(13.7)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0004",
        value="13",
    )
    assert virtual_energy_battery.imported_total == 13

    """Negative values should return 0"""
    await virtual_energy_battery.set_imported_total(-3.4)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0004",
        value="0",
    )
    assert virtual_energy_battery.imported_total == 0


@pytest.mark.asyncio
async def test_set_exported_total(virtual_energy_battery):
    """Test to set exported_total of the sensor."""
    """Values greater 0 should always work"""
    await virtual_energy_battery.set_exported_total(25)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0005",
        value="25",
    )
    assert virtual_energy_battery.exported_total == 25

    """Float values should return integer"""
    await virtual_energy_battery.set_exported_total(13.7)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0005",
        value="13",
    )
    assert virtual_energy_battery.exported_total == 13

    """Negative values should return 0"""
    await virtual_energy_battery.set_exported_total(-3.4)
    virtual_energy_battery._api.set_datapoint.assert_called_with(
        device_id="6000702DC087",
        channel_id="ch0002",
        datapoint="odp0005",
        value="0",
    )
    assert virtual_energy_battery.exported_total == 0


def test_update_device(virtual_energy_battery):
    """Test updating the device state."""

    def test_callback():
        pass

    # Ensure callback is registered to test callback code.
    virtual_energy_battery.register_callback(
        callback_attribute="soc", callback=test_callback
    )

    # Test scenario where websocket sends update not relevant to the state.
    virtual_energy_battery.update_device("AL_SWITCH_ON_OFF/odp0006", "1")
    assert virtual_energy_battery.soc == 0
