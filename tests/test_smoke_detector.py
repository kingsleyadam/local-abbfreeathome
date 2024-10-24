"""Test class to test the SmokeDetector device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.smoke_detector import SmokeDetector


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def smoke_detector(mock_api):
    """Set up the smoke-detector instance for testing the SmokeDetector device."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 707, "value": "0"},
        "odp0001": {"pairingID": 4, "value": "0"},
    }
    parameters = {}

    return SmokeDetector(
        device_id="E11244221190",
        device_name="Device Name",
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_initial_state(smoke_detector):
    """Test the intial state of the smoke-detector."""
    assert smoke_detector.state is False


@pytest.mark.asyncio
async def test_refresh_state(smoke_detector):
    """Test refreshing the state of the smoke-detector."""
    smoke_detector._api.get_datapoint.return_value = ["1"]
    await smoke_detector.refresh_state()
    assert smoke_detector.state is True
    smoke_detector._api.get_datapoint.assert_called_with(
        device_id="E11244221190",
        channel_id="ch0000",
        datapoint="odp0000",
    )


def test_refresh_state_from_output(smoke_detector):
    """Test the _refresh_state_from_output function."""
    # Check output that affects the state.
    smoke_detector._refresh_state_from_output(
        output={"pairingID": 707, "value": "1"},
    )
    assert smoke_detector.state is True

    # Check output that does NOT affect the state.
    smoke_detector._refresh_state_from_output(
        output={"pairingID": 4, "value": "1"},
    )
    assert smoke_detector.state is True
