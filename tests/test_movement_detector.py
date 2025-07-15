"""Test class to test the SwitchActuator channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.movement_detector import MovementDetector
from src.abbfreeathome.device import Device


def get_movement_detector(type: str, mock_api, mock_device):
    """Get the MovementDetector class to be tested against."""
    inputs = {"idp0000": {"pairingID": 256, "value": "0"}}
    outputs = {
        "odp0000": {"pairingID": 6, "value": "0"},
        "odp0001": {"pairingID": 7, "value": "0"},
        "odp0002": {"pairingID": 1027, "value": "1.6"},
    }
    parameters = {"par0034": "1", "par00d5": "100"}

    # If it's outdoor it won't have brightness
    if type == "outdoor":
        outputs.pop("odp0002")

    mock_device.device_serial = "ABB7F500E17A"
    mock_device.api = mock_api

    return MovementDetector(
        device=mock_device,
        channel_id="ch0003",
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
def movement_detector_indoor(mock_api, mock_device):
    """Set up the switch instance for testing the SwitchActuator channel."""
    return get_movement_detector("indoor", mock_api, mock_device)


@pytest.fixture
def movement_detector_outdoor(mock_api, mock_device):
    """Set up the switch instance for testing the SwitchActuator channel."""
    return get_movement_detector("outdoor", mock_api, mock_device)


@pytest.fixture
def mock_device():
    """Create a mock device function."""
    return MagicMock(spec=Device)


@pytest.mark.asyncio
async def test_initial_state_indoor(movement_detector_indoor):
    """Test the intial state."""
    assert movement_detector_indoor.state is False
    assert movement_detector_indoor.brightness == 1.6


@pytest.mark.asyncio
async def test_initial_state_outdoor(movement_detector_outdoor):
    """Test the intial state."""
    assert movement_detector_outdoor.state is False
    assert movement_detector_outdoor.brightness is None


@pytest.mark.asyncio
async def test_refresh_state(movement_detector_indoor):
    """Test refreshing the state."""
    movement_detector_indoor.device.api.get_datapoint.return_value = ["1"]
    await movement_detector_indoor.refresh_state()
    assert movement_detector_indoor.state is True
    assert movement_detector_indoor.brightness == 1.0
    movement_detector_indoor.device.api.get_datapoint.assert_called_with(
        device_serial="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="odp0000",
    )


def test_refresh_state_from_datapoint(movement_detector_indoor):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the state.
    movement_detector_indoor._refresh_state_from_datapoint(
        datapoint={"pairingID": 6, "value": "1"},
    )
    assert movement_detector_indoor.state is True

    # Check output that affects the state.
    movement_detector_indoor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1027, "value": "52.3"},
    )
    assert movement_detector_indoor.brightness == 52.3

    # Check output that does NOT affect the state.
    movement_detector_indoor._refresh_state_from_datapoint(
        datapoint={"pairingID": 6, "value": "0"},
    )
    assert movement_detector_indoor.brightness == 52.3
