"""Test class to test the CarbonMonoxideSensor device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.carbon_monoxide_sensor import CarbonMonoxideSensor


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def carbon_monoxide_sensor(mock_api):
    """Set up the sensor instance for testing the CarbonMonoxideSensor device."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 708, "value": "0"},
        "odp0001": {"pairingID": 4, "value": "0"},
    }
    parameters = {}

    return CarbonMonoxideSensor(
        device_id="E11253502766",
        device_name="Device Name",
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_initial_state(carbon_monoxide_sensor):
    """Test the intial state of the carbon-monoxide-sensor."""
    assert carbon_monoxide_sensor.state is False


@pytest.mark.asyncio
async def test_refresh_state(carbon_monoxide_sensor):
    """Test refreshing the state of the carbon-monoxide-sensor."""
    carbon_monoxide_sensor._api.get_datapoint.return_value = ["1"]
    await carbon_monoxide_sensor.refresh_state()
    assert carbon_monoxide_sensor.state is True
    carbon_monoxide_sensor._api.get_datapoint.assert_called_with(
        device_id="E11253502766",
        channel_id="ch0000",
        datapoint="odp0000",
    )


def test_refresh_state_from_datapoint(carbon_monoxide_sensor):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the state.
    carbon_monoxide_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 708, "value": "1"},
    )
    assert carbon_monoxide_sensor.state is True

    # Check output that does NOT affect the state.
    carbon_monoxide_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 4, "value": "1"},
    )
    assert carbon_monoxide_sensor.state is True
