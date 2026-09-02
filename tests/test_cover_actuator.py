"""Test class to test the CoverActuator channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.cover_actuator import (
    AwningActuator,
    CoverActuator,
    CoverActuatorForcedPosition,
    CoverActuatorState,
    ShutterActuator,
)
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
def cover_actuator(mock_api, mock_device):
    """Set up the generic cover instance for testing the CoverActuator channel."""
    inputs = {
        "idp0000": {"pairingID": 32, "value": "0"},
        "idp0001": {"pairingID": 33, "value": "1"},
        "idp0002": {"pairingID": 35, "value": "70"},
        "idp0003": {"pairingID": 36, "value": "0"},
        "idp0004": {"pairingID": 40, "value": "0"},
        "idp0005": {"pairingID": 37, "value": "0"},
        "idp0006": {"pairingID": 39, "value": "0"},
        "idp0007": {"pairingID": 38, "value": "0"},
        "idp0008": {"pairingID": 4, "value": "0"},
        "idp0009": {"pairingID": 53, "value": "0"},
    }
    outputs = {
        "odp0000": {"pairingID": 288, "value": "0"},
        "odp0001": {"pairingID": 289, "value": "0"},
        "odp0002": {"pairingID": 290, "value": "8"},
        "odp0003": {"pairingID": 273, "value": "0"},
        "odp0004": {"pairingID": 257, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "ABB2AC253651"
    mock_device.api = mock_api
    return CoverActuator(
        device=mock_device,
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.fixture
def shutter_actuator(mock_api, mock_device):
    """Set up the shutter actuator instance for testing the ShutterActuator channel."""
    inputs = {
        "idp0000": {"pairingID": 32, "value": "0"},
        "idp0001": {"pairingID": 33, "value": "1"},
        "idp0002": {"pairingID": 35, "value": "70"},
        "idp0003": {"pairingID": 36, "value": "0"},
        "idp0004": {"pairingID": 40, "value": "0"},
        "idp0005": {"pairingID": 37, "value": "0"},
        "idp0006": {"pairingID": 39, "value": "0"},
        "idp0007": {"pairingID": 38, "value": "0"},
        "idp0008": {"pairingID": 4, "value": "0"},
        "idp0009": {"pairingID": 53, "value": "0"},
    }
    outputs = {
        "odp0000": {"pairingID": 288, "value": "0"},
        "odp0001": {"pairingID": 289, "value": "0"},
        "odp0002": {"pairingID": 290, "value": "8"},
        "odp0003": {"pairingID": 273, "value": "0"},
        "odp0004": {"pairingID": 257, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "ABB2AC253651"
    mock_device.api = mock_api
    return ShutterActuator(
        device=mock_device,
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.fixture
def awning_actuator(mock_api, mock_device):
    """Set up the awning actuator instance for testing the AwningActuator channel."""
    inputs = {
        "idp0000": {"pairingID": 32, "value": "0"},
        "idp0001": {"pairingID": 33, "value": "1"},
        "idp0002": {"pairingID": 35, "value": "70"},
        "idp0003": {"pairingID": 36, "value": "0"},
        "idp0004": {"pairingID": 40, "value": "0"},
        "idp0005": {"pairingID": 37, "value": "0"},
        "idp0006": {"pairingID": 39, "value": "0"},
        "idp0007": {"pairingID": 38, "value": "0"},
        "idp0008": {"pairingID": 4, "value": "0"},
        "idp0009": {"pairingID": 53, "value": "0"},
    }
    outputs = {
        "odp0000": {"pairingID": 288, "value": "0"},
        "odp0001": {"pairingID": 289, "value": "0"},
        "odp0002": {"pairingID": 290, "value": "8"},
        "odp0003": {"pairingID": 273, "value": "0"},
        "odp0004": {"pairingID": 257, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "ABB2AC253651"
    mock_device.api = mock_api
    return AwningActuator(
        device=mock_device,
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_initial_state(cover_actuator):
    """Test the intial state of the RTC."""
    assert cover_actuator.state == CoverActuatorState.opened.name


@pytest.mark.asyncio
async def test_open(cover_actuator):
    """Test to open the cover."""
    await cover_actuator.open()
    cover_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0000",
        value="0",
    )


@pytest.mark.asyncio
async def test_close(cover_actuator):
    """Test to close the cover."""
    await cover_actuator.close()
    cover_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0000",
        value="1",
    )


@pytest.mark.asyncio
async def test_stop(cover_actuator):
    """Test to stop the cover."""
    interim = cover_actuator._state
    cover_actuator._state = CoverActuatorState.opening
    await cover_actuator.stop()
    cover_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0001",
        value="1",
    )
    cover_actuator._state = interim


@pytest.mark.asyncio
async def test_stop_when_not_moving(cover_actuator):
    """Test to stop the cover when it's not moving (should not call set_datapoint)."""
    # Set the cover state to something other than opening or closing
    cover_actuator._state = CoverActuatorState.opened

    # Reset the mock to ensure clean state
    cover_actuator.device.api.set_datapoint.reset_mock()

    # Call stop - this should hit the else branch (102->exit) and not call set_datapoint
    await cover_actuator.stop()

    # Verify that set_datapoint was NOT called
    cover_actuator.device.api.set_datapoint.assert_not_called()


@pytest.mark.asyncio
async def test_stop_when_closed(cover_actuator):
    """Test to stop the cover when it's in closed state (no set_datapoint call)."""
    # Set the cover state to closed
    cover_actuator._state = CoverActuatorState.unknown

    # Reset the mock to ensure clean state
    cover_actuator.device.api.set_datapoint.reset_mock()

    # Call stop - this should hit the else branch and not call set_datapoint
    await cover_actuator.stop()

    # Verify that set_datapoint was NOT called
    cover_actuator.device.api.set_datapoint.assert_not_called()


@pytest.mark.asyncio
async def test_set_forced_position(cover_actuator):
    """Test to force a position of a cover."""
    await cover_actuator.set_forced_position(
        CoverActuatorForcedPosition.deactivated.name
    )
    assert (
        cover_actuator.forced_position == CoverActuatorForcedPosition.deactivated.name
    )
    cover_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0004",
        value="0",
    )

    await cover_actuator.set_forced_position(
        CoverActuatorForcedPosition.forced_open.name
    )
    assert (
        cover_actuator.forced_position == CoverActuatorForcedPosition.forced_open.name
    )
    cover_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0004",
        value="2",
    )

    await cover_actuator.set_forced_position(
        CoverActuatorForcedPosition.forced_closed.name
    )
    assert (
        cover_actuator.forced_position == CoverActuatorForcedPosition.forced_closed.name
    )
    cover_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0004",
        value="3",
    )

    await cover_actuator.set_forced_position("INVALID")
    assert cover_actuator.forced_position == CoverActuatorForcedPosition.unknown.name


@pytest.mark.asyncio
async def test_set_position(cover_actuator):
    """Test to set a specific position of the blind."""
    await cover_actuator.set_position(50)
    cover_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0002",
        value="50",
    )
    assert cover_actuator.position == 50

    # Also checking lower and upper boundaries
    await cover_actuator.set_position(-1)
    cover_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0002",
        value="0",
    )
    assert cover_actuator.position == 0
    await cover_actuator.set_position(120)
    cover_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0002",
        value="100",
    )
    assert cover_actuator.position == 100


@pytest.mark.asyncio
async def test_set_tilt_position(shutter_actuator):
    """Test to set a specific tilt of the shutter."""
    await shutter_actuator.set_tilt_position(50)
    shutter_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0003",
        value="50",
    )
    assert shutter_actuator.tilt_position == 50

    # Also checking lower and upper boundaries
    await shutter_actuator.set_tilt_position(-1)
    shutter_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0003",
        value="0",
    )
    assert shutter_actuator.tilt_position == 0
    await shutter_actuator.set_tilt_position(120)
    shutter_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0003",
        value="100",
    )
    assert shutter_actuator.tilt_position == 100


@pytest.mark.asyncio
async def test_refresh_state_from_datapoint(shutter_actuator):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the state
    shutter_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 288, "value": "1"},
    )
    assert shutter_actuator.state == CoverActuatorState.partly_opened.name

    shutter_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 288, "value": "4"},
    )
    assert shutter_actuator.state == CoverActuatorState.unknown.name

    # Check output that affects the forced position
    shutter_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 257, "value": "2"}
    )
    assert (
        shutter_actuator.forced_position == CoverActuatorForcedPosition.forced_open.name
    )

    shutter_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 257, "value": "4"}
    )
    assert shutter_actuator.forced_position == CoverActuatorForcedPosition.unknown.name

    # Check output that affects the position
    shutter_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 289, "value": "35"}
    )
    assert shutter_actuator.position == 35

    # Check output that affects the position with a float value
    shutter_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 289, "value": "2.35294"}
    )
    assert shutter_actuator.position == 2

    # Check output that affects the tilt
    shutter_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 290, "value": "45"}
    )
    assert shutter_actuator._tilt_position == 45

    # Check output that affects the tile with a float value
    shutter_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 290, "value": "4.9"}
    )
    assert shutter_actuator._tilt_position == 4

    # Check output that does NOT affects the RTC
    shutter_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 0, "value": "1"},
    )
    assert shutter_actuator.position == 2


@pytest.mark.asyncio
async def test_is_closed(cover_actuator):
    """Test the is_closed property reflects the position."""
    cover_actuator._position = None
    assert cover_actuator.is_closed is None

    cover_actuator._position = 100
    assert cover_actuator.is_closed is True

    cover_actuator._position = 0
    assert cover_actuator.is_closed is False

    cover_actuator._position = 40
    assert cover_actuator.is_closed is False


@pytest.mark.asyncio
async def test_is_opening_is_closing(cover_actuator):
    """Test the is_opening and is_closing properties reflect the state."""
    cover_actuator._state = CoverActuatorState.opening
    assert cover_actuator.is_opening is True
    assert cover_actuator.is_closing is False

    cover_actuator._state = CoverActuatorState.closing
    assert cover_actuator.is_opening is False
    assert cover_actuator.is_closing is True

    cover_actuator._state = CoverActuatorState.opened
    assert cover_actuator.is_opening is False
    assert cover_actuator.is_closing is False


@pytest.mark.asyncio
async def test_awning_state_inverted(awning_actuator):
    """Test the moving direction is inverted for awnings."""
    # Raw opening ("2") -> public closing
    awning_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 288, "value": "2"}
    )
    assert awning_actuator.state == CoverActuatorState.closing.name
    assert awning_actuator.is_closing is True
    assert awning_actuator.is_opening is False

    # Raw closing ("3") -> public opening
    awning_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 288, "value": "3"}
    )
    assert awning_actuator.state == CoverActuatorState.opening.name
    assert awning_actuator.is_opening is True
    assert awning_actuator.is_closing is False

    # Non-directional state is unchanged
    awning_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 288, "value": "0"}
    )
    assert awning_actuator.state == CoverActuatorState.opened.name


@pytest.mark.asyncio
async def test_awning_is_closed(awning_actuator):
    """Test is_closed uses the inverted public position for awnings."""
    # Raw 0 (retracted) -> public 100 -> closed
    awning_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 289, "value": "0"}
    )
    assert awning_actuator.position == 100
    assert awning_actuator.is_closed is True

    # Raw 100 (extended) -> public 0 -> open
    awning_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 289, "value": "100"}
    )
    assert awning_actuator.position == 0
    assert awning_actuator.is_closed is False


@pytest.mark.asyncio
async def test_awning_open(awning_actuator):
    """Test opening (extending) the awning: public position 0 -> raw 100."""
    await awning_actuator.open()
    awning_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0002",
        value="100",
    )
    assert awning_actuator.position == 0


@pytest.mark.asyncio
async def test_awning_close(awning_actuator):
    """Test closing (retracting) the awning: public position 100 -> raw 0."""
    await awning_actuator.close()
    awning_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0002",
        value="0",
    )
    assert awning_actuator.position == 100


@pytest.mark.asyncio
async def test_awning_set_position(awning_actuator):
    """Test set_position inverts the public value to the raw Free@Home value."""
    await awning_actuator.set_position(30)
    awning_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0002",
        value="70",
    )
    assert awning_actuator.position == 30

    # Boundaries
    await awning_actuator.set_position(-1)
    awning_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0002",
        value="100",
    )
    assert awning_actuator.position == 0

    await awning_actuator.set_position(120)
    awning_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0002",
        value="0",
    )
    assert awning_actuator.position == 100


@pytest.mark.asyncio
async def test_awning_refresh_position_inverted(awning_actuator):
    """Test the raw Free@Home position is inverted to the public value."""
    # Raw 100 (extended) -> public 0 (open)
    awning_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 289, "value": "100"}
    )
    assert awning_actuator.position == 0

    # Raw 30 -> public 70
    awning_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 289, "value": "30"}
    )
    assert awning_actuator.position == 70

    # A non-position datapoint should not affect the position
    awning_actuator._refresh_state_from_datapoint(
        datapoint={"pairingID": 0, "value": "1"}
    )
    assert awning_actuator.position == 70
