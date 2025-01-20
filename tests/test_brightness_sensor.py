"""Test class to test the BrightnessSensor device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.brightness_sensor import BrightnessSensor


def get_brightness_sensor(mock_api):
    """Get the BrightnessSensor class to be tested against."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 1026, "value": "0"},
        "odp0001": {"pairingID": 1027, "value": "300.50"},
    }
    parameters = {"par002b": "19998.7", "par002c": "4999.68"}

    return BrightnessSensor(
        device_id="7EB1000021C5",
        device_name="Device Name",
        channel_id="ch0000",
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
def brightness_sensor(mock_api):
    """Set up the instance for testing the BrightnessSensor device."""
    return get_brightness_sensor(mock_api)


@pytest.mark.asyncio
async def test_initial_state(brightness_sensor):
    """Test the intial state of the sensor."""
    assert brightness_sensor.state == 300.50
    assert brightness_sensor.alarm is False


@pytest.mark.asyncio
async def test_refresh_state(brightness_sensor):
    """Test refreshing the state of the sensor."""
    brightness_sensor._api.get_datapoint.return_value = ["1"]
    await brightness_sensor.refresh_state()
    assert brightness_sensor.state == 1.0
    assert brightness_sensor.alarm is True
    brightness_sensor._api.get_datapoint.assert_called_with(
        device_id="7EB1000021C5",
        channel_id="ch0000",
        datapoint="odp0000",
    )


def test_refresh_state_from_datapoint(brightness_sensor):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the state.
    brightness_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1027, "value": "50.7"},
    )
    assert brightness_sensor.state == 50.7

    # Check output that affects the state.
    brightness_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1026, "value": "1"},
    )
    assert brightness_sensor.alarm is True

    # Check output that does NOT affect the state.
    brightness_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 4, "value": "1"},
    )
    assert brightness_sensor.state == 50.7
