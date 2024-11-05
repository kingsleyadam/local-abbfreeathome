"""Test class to test the HeatingActuator devices."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.heating_actuator import HeatingActuator


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def heating_actuator(mock_api):
    """Set up the heating actuator instance for testing the HeatingActuator device."""
    inputs = {
        "idp0000": {"pairingID": 48, "value": "0"}  # AL_ACTUATING_VALUE_HEATING
    }
    outputs = {
        "odp0000": {"pairingID": 305, "value": "0"},  # AL_INFO_VALUE_HEATING
        "odp0002": {"pairingID": 273, "value": "0"},
    }
    parameters = {}

    return HeatingActuator(
        device_id="ABB289613651",
        device_name="Device Name",
        channel_id="ch0002",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_initial_state(heating_actuator):
    """Test the intial state of the HeatingActuator."""
    assert heating_actuator.position == 0


@pytest.mark.asyncio
async def test_set_position(heating_actuator):
    """Test to set a specific position of the HeatingActuator."""
    await heating_actuator.set_position(50)
    heating_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB289613651",
        channel_id="ch0002",
        datapoint="idp0000",
        value="50",
    )
    assert heating_actuator.position == 50

    # Also checking lower and upper boundaries
    await heating_actuator.set_position(-1)
    heating_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB289613651",
        channel_id="ch0002",
        datapoint="idp0000",
        value="0",
    )
    assert heating_actuator.position == 0
    await heating_actuator.set_position(120)
    heating_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB289613651",
        channel_id="ch0002",
        datapoint="idp0000",
        value="100",
    )
    assert heating_actuator.position == 100


@pytest.mark.asyncio
async def test_refresh_state_from_output(heating_actuator):
    """Test the _refresh_state_from_output function."""
    # Check output that affects the position
    heating_actuator._refresh_state_from_output(
        output={"pairingID": 305, "value": "35"}
    )
    assert heating_actuator.position == 35

    # Check output that does NOT affects the position
    heating_actuator._refresh_state_from_output(
        output={"pairingID": 273, "value": "1"},
    )
    assert heating_actuator.position == 35
