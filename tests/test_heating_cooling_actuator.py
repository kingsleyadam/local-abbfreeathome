"""Test class to test the HeatingCoolingActuator channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.pairing import Pairing
from src.abbfreeathome.channels.valve_actuator import HeatingCoolingActuator
from src.abbfreeathome.device import Device


def get_heating_cooling_actuator(mock_api, mock_device):
    """Get the HeatingCoolingActuator class to be tested against."""
    # Set the api on the mock device so channels can access it
    mock_device.api = mock_api

    inputs = {
        "idp0000": {"pairingID": 48, "value": "81"},  # AL_ACTUATING_VALUE_HEATING
        "idp0001": {"pairingID": 50, "value": "0"},  # AL_ACTUATING_VALUE_COOLING
        "idp0002": {"pairingID": 309, "value": "1"},  # AL_HEATING_COOLING
    }
    outputs = {
        "odp0000": {"pairingID": 305, "value": "81"},  # AL_INFO_VALUE_HEATING
        "odp0001": {"pairingID": 306, "value": "0"},  # AL_INFO_VALUE_COOLING
        "odp0002": {"pairingID": 273, "value": "0"},  # AL_INFO_ERROR
    }
    parameters = {
        "par002f": "1",  # PID_CONTACT_TYPE
        "par0030": "0",  # PID_BEHAVIOUR_ON_MALFUNCTION_HEATING
        "par00ff": "900",  # PID_HEATING_ACTUATOR_PAUSE_TIME
    }

    return HeatingCoolingActuator(
        device=mock_device,
        channel_id="ch0003",
        channel_name="Büro Ingmar",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def heating_cooling_actuator(mock_api, mock_device):
    """Set up the instance for testing the HeatingCoolingActuator channel."""
    mock_device.device_serial = "ABB277BB4651"
    return get_heating_cooling_actuator(mock_api, mock_device)


@pytest.fixture
def mock_device():
    """Create a mock device function."""
    return MagicMock(spec=Device)


@pytest.mark.asyncio
async def test_initial_state(heating_cooling_actuator):
    """Test the initial state of the actuator."""
    assert heating_cooling_actuator.heating_position == 81
    assert heating_cooling_actuator.cooling_position == 0


@pytest.mark.asyncio
async def test_set_heating_position(heating_cooling_actuator):
    """Test setting the heating position."""
    heating_cooling_actuator.device.api.set_datapoint.return_value = None
    await heating_cooling_actuator.set_heating_position(75)

    assert heating_cooling_actuator.heating_position == 75
    heating_cooling_actuator.device.api.set_datapoint.assert_called_once_with(
        device_serial="ABB277BB4651",
        channel_id="ch0003",
        datapoint="idp0000",
        value="75",
    )


@pytest.mark.asyncio
async def test_set_heating_position_bounds(heating_cooling_actuator):
    """Test setting the heating position with boundary values."""
    heating_cooling_actuator.device.api.set_datapoint.return_value = None

    # Test upper bound
    await heating_cooling_actuator.set_heating_position(150)
    assert heating_cooling_actuator.heating_position == 100

    # Test lower bound
    await heating_cooling_actuator.set_heating_position(-10)
    assert heating_cooling_actuator.heating_position == 0


@pytest.mark.asyncio
async def test_set_cooling_position(heating_cooling_actuator):
    """Test setting the cooling position."""
    heating_cooling_actuator.device.api.set_datapoint.return_value = None
    await heating_cooling_actuator.set_cooling_position(50)

    assert heating_cooling_actuator.cooling_position == 50
    heating_cooling_actuator.device.api.set_datapoint.assert_called_once_with(
        device_serial="ABB277BB4651",
        channel_id="ch0003",
        datapoint="idp0001",
        value="50",
    )


@pytest.mark.asyncio
async def test_set_cooling_position_bounds(heating_cooling_actuator):
    """Test setting the cooling position with boundary values."""
    heating_cooling_actuator.device.api.set_datapoint.return_value = None

    # Test upper bound
    await heating_cooling_actuator.set_cooling_position(150)
    assert heating_cooling_actuator.cooling_position == 100

    # Test lower bound
    await heating_cooling_actuator.set_cooling_position(-10)
    assert heating_cooling_actuator.cooling_position == 0


@pytest.mark.asyncio
async def test_refresh_state(heating_cooling_actuator):
    """Test refreshing the state of the actuator."""
    # Mock the API to return different values for each pairing
    heating_cooling_actuator.device.api.get_datapoint.side_effect = [
        ["65"],  # Heating position
        ["25"],  # Cooling position
    ]

    await heating_cooling_actuator.refresh_state()

    assert heating_cooling_actuator.heating_position == 65
    assert heating_cooling_actuator.cooling_position == 25


def test_refresh_state_from_datapoint_heating(heating_cooling_actuator):
    """Test the _refresh_state_from_datapoint function for heating."""
    result = heating_cooling_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 305, "value": "50"},
    )
    assert result == "heating_position"
    assert heating_cooling_actuator.heating_position == 50


def test_refresh_state_from_datapoint_cooling(heating_cooling_actuator):
    """Test the _refresh_state_from_datapoint function for cooling."""
    result = heating_cooling_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 306, "value": "75"},
    )
    assert result == "cooling_position"
    assert heating_cooling_actuator.cooling_position == 75


def test_refresh_state_from_datapoint_invalid(heating_cooling_actuator):
    """Test the _refresh_state_from_datapoint function with invalid pairing."""
    # Check output that does NOT affect the state
    result = heating_cooling_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 9999, "value": "1"},
    )
    assert result is None
    # Ensure no state changed
    assert heating_cooling_actuator.heating_position == 81
    assert heating_cooling_actuator.cooling_position == 0


def test_all_properties(heating_cooling_actuator):
    """Test all properties return expected values."""
    assert heating_cooling_actuator.heating_position == 81
    assert heating_cooling_actuator.cooling_position == 0


def test_callback_attributes(heating_cooling_actuator):
    """Test that callback attributes are properly defined."""
    assert "heating_position" in heating_cooling_actuator._callback_attributes
    assert "cooling_position" in heating_cooling_actuator._callback_attributes


def test_state_refresh_pairings(heating_cooling_actuator):
    """Test that state refresh pairings are properly defined."""
    assert (
        Pairing.AL_INFO_VALUE_HEATING
        in heating_cooling_actuator._state_refresh_pairings
    )
    assert (
        Pairing.AL_INFO_VALUE_COOLING
        in heating_cooling_actuator._state_refresh_pairings
    )


def test_heating_position_with_float_value(heating_cooling_actuator):
    """Test heating position handles float values correctly."""
    result = heating_cooling_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 305, "value": "75.5"},
    )
    assert result == "heating_position"
    assert heating_cooling_actuator.heating_position == 75


def test_cooling_position_with_float_value(heating_cooling_actuator):
    """Test cooling position handles float values correctly."""
    result = heating_cooling_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 306, "value": "50.7"},
    )
    assert result == "cooling_position"
    assert heating_cooling_actuator.cooling_position == 50
