"""Test class to test the Trigger device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.trigger import Trigger


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def trigger(mock_api):
    """Set up the trigger instance for testing the Trigger device."""
    inputs = {
        "idp0001": {"pairingID": 2, "value": "1"},
        "idp0003": {"pairingID": 4, "value": "0"},
    }
    outputs = {}
    parameters = {}

    return Trigger(
        device_id="ABB28EBC3651",
        device_name="Device Name",
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_press(trigger):
    """Test to press the trigger."""
    await trigger.press()
    trigger._api.set_datapoint.assert_called_with(
        device_id="ABB28EBC3651",
        channel_id="ch0003",
        datapoint="idp0001",
        value="1",
    )
