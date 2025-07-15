"""Test class to test the DesDoorRingingSensor channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.des_door_ringing_sensor import DesDoorRingingSensor
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
def des_door_ringing_sensor(mock_api, mock_device):
    """Set up the sensor instance for testing the DesDoorRingingSensor channel."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 2, "value": "1"},
        "odp0001": {"pairingID": 4, "value": "0"},
    }
    parameters = {}

    return DesDoorRingingSensor(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


def test_refresh_state_from_datapoint(des_door_ringing_sensor):
    """Test the _refresh_state_from_datapoint function."""
    assert (
        des_door_ringing_sensor._refresh_state_from_datapoint(
            datapoint={"pairingID": 2, "value": "1"},
        )
        == "state"
    )
    assert (
        des_door_ringing_sensor._refresh_state_from_datapoint(
            datapoint={"pairingID": 4, "value": "1"},
        )
        is None
    )
