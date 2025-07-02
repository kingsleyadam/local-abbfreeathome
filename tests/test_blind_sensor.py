"""Test class to test the BlindSensor channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.blind_sensor import BlindSensor, BlindSensorState
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
def blind_sensor(mock_api, mock_device):
    """Set up the blind-sensor instance for testing the BlindSensor channel."""
    inputs = {}
    outputs = {
        "odp0002": {"pairingID": 32, "value": "0"},  # AL_MOVE_UP_DOWN
        "odp0003": {"pairingID": 33, "value": "0"},  # AL_STOP_STEP_UP_DOWN
        "odp0006": {"pairingID": 4, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "ABB700DAD681"

    mock_device.api = mock_api
    return BlindSensor(
        device=mock_device,
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_initial_state(blind_sensor):
    """Test the intial state of the blind-sensor."""
    assert blind_sensor.state == BlindSensorState.step_up.name


@pytest.mark.asyncio
async def test_refresh_state(blind_sensor):
    """Test refreshing the state of the blind-sensor."""
    blind_sensor.device.api.get_datapoint.return_value = ["1"]
    await blind_sensor.refresh_state()
    assert blind_sensor.state == BlindSensorState.step_down.name
    blind_sensor.device.api.get_datapoint.assert_called_with(
        device_serial="ABB700DAD681",
        channel_id="ch0003",
        datapoint="odp0003",
    )


def test_refresh_state_from_datapoint(blind_sensor):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the state.
    blind_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 33, "value": "1"},
    )
    assert blind_sensor.state == BlindSensorState.step_down.name
    assert blind_sensor.step_state == BlindSensorState.step_down.name

    blind_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 32, "value": "1"},
    )
    assert blind_sensor.state == BlindSensorState.move_down.name
    assert blind_sensor.move_state == BlindSensorState.move_down.name

    # Test unknown values
    blind_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 32, "value": "INVALID"},
    )
    assert blind_sensor.state == BlindSensorState.unknown.name
    assert blind_sensor.move_state == BlindSensorState.unknown.name

    blind_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 33, "value": "INVALID"},
    )
    assert blind_sensor.state == BlindSensorState.unknown.name
    assert blind_sensor.step_state == BlindSensorState.unknown.name
