"""Test class to test the SwitchActuator device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.movement_detector import MovementDetector


def get_movement_detector(type: str, mock_api):
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

    return MovementDetector(
        device_id="ABB7F500E17A",
        device_name="Device Name",
        channel_id="ch0003",
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
def movement_detector_indoor(mock_api):
    """Set up the switch instance for testing the SwitchActuator device."""
    return get_movement_detector("indoor", mock_api)


@pytest.fixture
def movement_detector_outdoor(mock_api):
    """Set up the switch instance for testing the SwitchActuator device."""
    return get_movement_detector("outdoor", mock_api)


@pytest.mark.asyncio
async def test_initial_state_indoor(movement_detector_indoor):
    """Test the intial state of the switch."""
    assert movement_detector_indoor.state is False
    assert movement_detector_indoor.brightness == 1.6


@pytest.mark.asyncio
async def test_initial_state_outdoor(movement_detector_outdoor):
    """Test the intial state of the switch."""
    assert movement_detector_outdoor.state is False
    assert movement_detector_outdoor.brightness is None


@pytest.mark.asyncio
async def test_refresh_state(movement_detector_indoor):
    """Test refreshing the state of the switch."""
    movement_detector_indoor._api.get_datapoint.return_value = ["1"]
    await movement_detector_indoor.refresh_state()
    assert movement_detector_indoor.state is True
    assert movement_detector_indoor.brightness == 1.0
    movement_detector_indoor._api.get_datapoint.assert_called_with(
        device_id="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="odp0000",
    )


def test_refresh_state_from_output(movement_detector_indoor):
    """Test the _refresh_state_from_output function."""
    # Check output that affects the state.
    movement_detector_indoor._refresh_state_from_output(
        output={"pairingID": 6, "value": "1"},
    )
    assert movement_detector_indoor.state is True

    # Check output that affects the state.
    movement_detector_indoor._refresh_state_from_output(
        output={"pairingID": 1027, "value": "52.3"},
    )
    assert movement_detector_indoor.brightness == 52.3

    # Check output that does NOT affect the state.
    movement_detector_indoor._refresh_state_from_output(
        output={"pairingID": 6, "value": "0"},
    )
    assert movement_detector_indoor.brightness == 52.3
