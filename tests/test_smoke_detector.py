"""Test class to test the SmokeDetector channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.smoke_detector import SmokeDetector
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
def smoke_detector(mock_api, mock_device):
    """Set up the smoke-detector instance for testing the SmokeDetector channel."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 707, "value": "0"},
        "odp0001": {"pairingID": 4, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "E11244221190"

    mock_device.api = mock_api
    return SmokeDetector(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_initial_state(smoke_detector):
    """Test the intial state of the smoke-detector."""
    assert smoke_detector.state is False


@pytest.mark.asyncio
async def test_refresh_state(smoke_detector):
    """Test refreshing the state of the smoke-detector."""
    smoke_detector.device.api.get_datapoint.return_value = ["1"]
    await smoke_detector.refresh_state()
    assert smoke_detector.state is True
    smoke_detector.device.api.get_datapoint.assert_called_with(
        device_serial="E11244221190",
        channel_id="ch0000",
        datapoint="odp0000",
    )


def test_refresh_state_from_datapoint(smoke_detector):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the state.
    smoke_detector._refresh_state_from_datapoint(
        datapoint={"pairingID": 707, "value": "1"},
    )
    assert smoke_detector.state is True

    # Check output that does NOT affect the state.
    smoke_detector._refresh_state_from_datapoint(
        datapoint={"pairingID": 4, "value": "1"},
    )
    assert smoke_detector.state is True
