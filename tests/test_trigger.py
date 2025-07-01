"""Test class to test the Trigger channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.trigger import Trigger
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
def trigger(mock_api, mock_device):
    """Set up the trigger instance for testing the Trigger channel."""
    inputs = {
        "idp0001": {"pairingID": 2, "value": "1"},
        "idp0003": {"pairingID": 4, "value": "0"},
    }
    outputs = {}
    parameters = {}

    mock_device.device_serial = "ABB28EBC3651"

    mock_device.api = mock_api
    return Trigger(
        device=mock_device,
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_press(trigger):
    """Test to press the trigger."""
    await trigger.press()
    trigger.device.api.set_datapoint.assert_called_with(
        device_serial="ABB28EBC3651",
        channel_id="ch0003",
        datapoint="idp0001",
        value="1",
    )
