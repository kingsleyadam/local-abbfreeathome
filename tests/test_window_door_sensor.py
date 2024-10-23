"""Test class to test the WindowDoorSensor device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.window_door_sensor import WindowDoorSensor


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def window_door_sensor(mock_api):
    """Set up the sensor instance for testing the WindowDoorSensor device."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 53, "value": "1"},
        "odp0001": {"pairingID": 0, "value": "0"},
        "odp0003": {"pairingID": 41, "value": "33"},
    }
    parameters = {"par0010": "2"}

    return WindowDoorSensor(
        device_id="ABB28CBC3651",
        device_name="Device Name",
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_initial_state(window_door_sensor):
    """Test the intial state of the window-door-sensor."""
    assert window_door_sensor.state is True
    assert window_door_sensor.position == "tilted"


@pytest.mark.asyncio
async def test_refresh_state(window_door_sensor):
    """Test refreshing the state of the window-door-sensor."""
    window_door_sensor._api.get_datapoint.return_value = ["1"]
    await window_door_sensor.refresh_state()
    assert window_door_sensor.state is True
    window_door_sensor._api.get_datapoint.assert_called_with(
        device_id="ABB28CBC3651",
        channel_id="ch0000",
        datapoint="odp0000",
    )


def test_refresh_state_from_output(window_door_sensor):
    """Test the _refresh_state_from_output function."""
    # Check output that affects the state.
    window_door_sensor._refresh_state_from_output(
        output={"pairingID": 53, "value": "0"},
    )
    assert window_door_sensor.state is False

    window_door_sensor._refresh_state_from_output(
        output={"pairingID": 41, "value": "100"},
    )
    assert window_door_sensor.position == "open"

    window_door_sensor._refresh_state_from_output(
        output={"pairingID": 41, "value": "NOTVALID"},
    )
    assert window_door_sensor.position == "unknown"

    # Check output that NOT affects the state.
    window_door_sensor._refresh_state_from_output(
        output={"pairingID": 0, "value": "1"},
    )
    assert window_door_sensor.state is False
