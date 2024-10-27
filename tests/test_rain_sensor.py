"""Test class to test the RainSensor device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.rain_sensor import RainSensor


def get_rain_sensor(mock_api):
    """Get the RainSensor class to be tested against."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 39, "value": "0"},
        "odp0001": {"pairingID": 4, "value": "0"},
        "odp0002": {"pairingID": 1029, "value": "0"},
        "odp0003": {"pairingID": 1030, "value": "0"},
    }
    parameters = {"par0049": "1", "par0047": "2", "par0048": "7"}

    return RainSensor(
        device_id="7EB1000021C5",
        device_name="Device Name",
        channel_id="ch0001",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def rain_sensor(mock_api):
    """Set up the instance for testing the RainSensor device."""
    return get_rain_sensor(mock_api)


@pytest.mark.asyncio
async def test_initial_state(rain_sensor):
    """Test the intial state of the sensor."""
    assert rain_sensor.state is False


@pytest.mark.asyncio
async def test_refresh_state(rain_sensor):
    """Test refreshing the state of the sensor."""
    rain_sensor._api.get_datapoint.return_value = ["1"]
    await rain_sensor.refresh_state()
    assert rain_sensor.state is True
    rain_sensor._api.get_datapoint.assert_called_with(
        device_id="7EB1000021C5",
        channel_id="ch0001",
        datapoint="odp0000",
    )


def test_refresh_state_from_output(rain_sensor):
    """Test the _refresh_state_from_output function."""
    # Check output that affects the state.
    rain_sensor._refresh_state_from_output(
        output={"pairingID": 39, "value": "1"},
    )
    assert rain_sensor.state is True

    # Check output that does NOT affect the state.
    rain_sensor._refresh_state_from_output(
        output={"pairingID": 4, "value": "1"},
    )
    assert rain_sensor.state is True
