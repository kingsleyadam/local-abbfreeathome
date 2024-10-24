"""Test class to test the DesDoorRingingSensor device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.des_door_ringing_sensor import DesDoorRingingSensor


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def des_door_ringing_sensor(mock_api):
    """Set up the sensor instance for testing the DesDoorRingingSensor device."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 2, "value": "1"},
        "odp0001": {"pairingID": 4, "value": "0"},
    }
    parameters = {}

    return DesDoorRingingSensor(
        device_id="0007EE9503A4",
        device_name="Device Name",
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


def test_refresh_state_from_output(des_door_ringing_sensor):
    """Test the _refresh_state_from_output function."""
    assert (
        des_door_ringing_sensor._refresh_state_from_output(
            output={"pairingID": 2, "value": "1"},
        )
        is True
    )
    assert (
        des_door_ringing_sensor._refresh_state_from_output(
            output={"pairingID": 4, "value": "1"},
        )
        is False
    )
