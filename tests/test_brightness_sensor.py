"""Test class to test the BrightnessSensor channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.brightness_sensor import BrightnessSensor
from src.abbfreeathome.device import Device


def get_brightness_sensor(mock_api, mock_device):
    """Get the BrightnessSensor class to be tested against."""
    # Set the api on the mock device so channels can access it
    mock_device.api = mock_api

    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 1026, "value": "0"},
        "odp0001": {"pairingID": 1027, "value": "300.50"},
    }
    parameters = {"par002b": "19998.7", "par002c": "4999.68"}

    return BrightnessSensor(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def brightness_sensor(mock_api, mock_device):
    """Set up the instance for testing the BrightnessSensor channel."""
    mock_device.device_serial = "7EB1000021C5"
    return get_brightness_sensor(mock_api, mock_device)


@pytest.fixture
def mock_device():
    """Create a mock device function."""
    return MagicMock(spec=Device)


@pytest.mark.asyncio
async def test_initial_state(brightness_sensor):
    """Test the intial state of the sensor."""
    assert brightness_sensor.state == 300.50
    assert brightness_sensor.alarm is False


@pytest.mark.asyncio
async def test_refresh_state(brightness_sensor):
    """Test refreshing the state of the sensor."""
    brightness_sensor.device.api.get_datapoint.return_value = ["1"]
    await brightness_sensor.refresh_state()
    assert brightness_sensor.state == 1.0
    assert brightness_sensor.alarm is True
    brightness_sensor.device.api.get_datapoint.assert_called_with(
        device_serial="7EB1000021C5",
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
