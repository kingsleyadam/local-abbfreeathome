"""Test class to test the ForceOnOffSensor channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.force_on_off_sensor import (
    ForceOnOffSensor,
    ForceOnOffSensorState,
)
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
def force_on_off_sensor(mock_api, mock_device):
    """Set up the force-on-off-sensor instance for testing the sensor channel."""
    inputs = {}
    outputs = {
        "odp0005": {"pairingID": 3, "value": "1"},
        "odp0006": {"pairingID": 4, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "ABB7F5923D74"

    mock_device.api = mock_api
    return ForceOnOffSensor(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_initial_state(force_on_off_sensor):
    """Test the intial state of the force-on-off-sensor."""
    assert force_on_off_sensor.state == ForceOnOffSensorState.off.name


@pytest.mark.asyncio
async def test_refresh_state(force_on_off_sensor):
    """Test refreshing the state of the force-on-off-sensor."""
    force_on_off_sensor.device.api.get_datapoint.return_value = ["1"]
    await force_on_off_sensor.refresh_state()
    assert force_on_off_sensor.state == ForceOnOffSensorState.off.name
    force_on_off_sensor.device.api.get_datapoint.assert_called_with(
        device_serial="ABB7F5923D74",
        channel_id="ch0000",
        datapoint="odp0005",
    )


def test_refresh_state_from_datapoint(force_on_off_sensor):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the state.
    force_on_off_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 3, "value": "0"},
    )
    assert force_on_off_sensor.state == ForceOnOffSensorState.off.name

    force_on_off_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 3, "value": "1"},
    )
    assert force_on_off_sensor.state == ForceOnOffSensorState.off.name

    force_on_off_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 3, "value": "2"},
    )
    assert force_on_off_sensor.state == ForceOnOffSensorState.on.name

    force_on_off_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 3, "value": "3"},
    )
    assert force_on_off_sensor.state == ForceOnOffSensorState.on.name

    force_on_off_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 3, "value": "INVALID"},
    )
    assert force_on_off_sensor.state == ForceOnOffSensorState.unknown.name
