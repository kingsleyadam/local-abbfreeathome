"""Test class to test the SwitchActuator device."""

from unittest.mock import AsyncMock

import pytest

from abbfreeathome.api import FreeAtHomeApi
from abbfreeathome.devices.movement_detector import MovementDetector


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def movement_detector(mock_api):
    """Set up the switch instance for testing the SwitchActuator device."""
    inputs = {"idp0000": {"pairingID": 256, "value": "0"}}
    outputs = {
        "odp0000": {"pairingID": 6, "value": "0"},
        "odp0001": {"pairingID": 7, "value": "0"},
        "odp0002": {"pairingID": 1027, "value": "1.6"},
    }
    parameters = {"par0034": "1", "par00d5": "100"}

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


@pytest.mark.asyncio
async def test_initial_state(movement_detector):
    """Test the intial state of the switch."""
    assert movement_detector.state is False
    assert movement_detector.brightness == 1.6


@pytest.mark.asyncio
async def test_refresh_state(movement_detector):
    """Test refreshing the state of the switch."""
    movement_detector._api.get_datapoint.return_value = ["1"]
    await movement_detector.refresh_state()
    assert movement_detector.state is True
    assert movement_detector.brightness == 1.0
    movement_detector._api.get_datapoint.assert_called_with(
        device_id="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="odp0000",
    )


def test_refresh_state_from_output(movement_detector):
    """Test the _refresh_state_from_output function."""
    # Check output that affects the state.
    movement_detector._refresh_state_from_output(
        output={"pairingID": 6, "value": "1"},
    )
    assert movement_detector.state is True

    # Check output that affects the state.
    movement_detector._refresh_state_from_output(
        output={"pairingID": 1027, "value": "52.3"},
    )
    assert movement_detector.brightness == 52.3

    # Check output that does NOT affect the state.
    movement_detector._refresh_state_from_output(
        output={"pairingID": 6, "value": "0"},
    )
    assert movement_detector.brightness == 52.3
