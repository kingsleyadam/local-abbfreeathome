"""Test class to test the CoolingActuator channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.valve_actuator import CoolingActuator
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
def cooling_actuator(mock_api, mock_device):
    """Set up the instance for testing the CoolingActuator channel."""
    mock_device.device_serial = "ABB277BB4651"
    mock_device.api = mock_api

    inputs = {
        "idp0000": {"pairingID": 50, "value": "75"},  # AL_ACTUATING_VALUE_COOLING
    }
    outputs = {
        "odp0000": {"pairingID": 306, "value": "75"},  # AL_INFO_VALUE_COOLING
    }
    parameters = {
        "par002f": "1",  # PID_CONTACT_TYPE
    }

    return CoolingActuator(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Test Cooling",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_initial_state(cooling_actuator):
    """Test the initial state of the cooling actuator."""
    assert cooling_actuator.position == 75


@pytest.mark.asyncio
async def test_set_position(cooling_actuator):
    """Test setting the cooling position."""
    cooling_actuator.device.api.set_datapoint.return_value = None
    await cooling_actuator.set_position(50)

    assert cooling_actuator.position == 50
    cooling_actuator.device.api.set_datapoint.assert_called_once_with(
        device_serial="ABB277BB4651",
        channel_id="ch0000",
        datapoint="idp0000",
        value="50",
    )


@pytest.mark.asyncio
async def test_set_position_bounds(cooling_actuator):
    """Test setting the cooling position with boundary values."""
    cooling_actuator.device.api.set_datapoint.return_value = None

    # Test upper bound
    await cooling_actuator.set_position(150)
    assert cooling_actuator.position == 100

    # Test lower bound
    await cooling_actuator.set_position(-10)
    assert cooling_actuator.position == 0


def test_refresh_state_from_datapoint(cooling_actuator):
    """Test the _refresh_state_from_datapoint function."""
    result = cooling_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 306, "value": "85"},
    )
    assert result == "position"
    assert cooling_actuator.position == 85


def test_refresh_state_from_datapoint_float(cooling_actuator):
    """Test cooling position handles float values correctly."""
    result = cooling_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 306, "value": "65.7"},
    )
    assert result == "position"
    assert cooling_actuator.position == 65


def test_refresh_state_from_datapoint_invalid(cooling_actuator):
    """Test that invalid pairing IDs are ignored."""
    result = cooling_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 999, "value": "50"},
    )
    assert result is None
    # Position should remain unchanged at 75
    assert cooling_actuator.position == 75
