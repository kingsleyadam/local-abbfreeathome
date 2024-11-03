"""Test class to test the CoverActuator devices."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.cover_actuator import CoverActuator, ShutterActuator


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def cover_actuator(mock_api):
    """Set up the generic cover instance for testing the CoverActuator device."""
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

    return CoverActuator(
        device_id="ABB2AC253651",
        device_name="Device Name",
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.fixture
def shutter_actuator(mock_api):
    """Set up the shutter actuator instance for testing the ShutterActuator device."""
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

    return ShutterActuator(
        device_id="ABB2AC253651",
        device_name="Device Name",
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_initial_state(cover_actuator):
    """Test the intial state of the RTC."""
    assert cover_actuator.state == 0


def test_is_cover_closed(cover_actuator):
    """Test to check if cover is closed."""
    interim = cover_actuator._position
    cover_actuator._position = 100
    assert cover_actuator.is_cover_closed() is True
    cover_actuator._position = 99
    assert cover_actuator.is_cover_closed() is False
    cover_actuator._position = interim


def test_is_cover_opening(cover_actuator):
    """Test to check if cover is opening."""
    interim = cover_actuator._state
    cover_actuator._state = 2
    assert cover_actuator.is_cover_opening() is True
    cover_actuator._state = 0
    assert cover_actuator.is_cover_opening() is False
    cover_actuator._state = interim


def test_is_cover_closing(cover_actuator):
    """Test to check if cover is closing."""
    interim = cover_actuator._state
    cover_actuator._state = 3
    assert cover_actuator.is_cover_closing() is True
    cover_actuator._state = 0
    assert cover_actuator.is_cover_closing() is False
    cover_actuator._state = interim


@pytest.mark.asyncio
async def test_open(cover_actuator):
    """Test to open the cover."""
    await cover_actuator.open()
    cover_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0000",
        value="0",
    )


@pytest.mark.asyncio
async def test_close(cover_actuator):
    """Test to close the cover."""
    await cover_actuator.close()
    cover_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0000",
        value="1",
    )


@pytest.mark.asyncio
async def test_stop(cover_actuator):
    """Test to stop the cover."""
    interim = cover_actuator._state
    cover_actuator._state = 2
    await cover_actuator.stop()
    cover_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0001",
        value="1",
    )
    cover_actuator._state = interim


@pytest.mark.asyncio
async def test_force_position(cover_actuator):
    """Test to force a position of a cover."""
    await cover_actuator.force_position(0)
    cover_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0004",
        value="0",
    )
    await cover_actuator.force_position(2)
    cover_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0004",
        value="2",
    )
    await cover_actuator.force_position(3)
    cover_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0004",
        value="3",
    )


@pytest.mark.asyncio
async def test_set_position(cover_actuator):
    """Test to set a specific position of the blind."""
    await cover_actuator.set_position(50)
    cover_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0002",
        value="50",
    )
    assert cover_actuator.position == 50

    # Also checking lower and upper boundaries
    await cover_actuator.set_position(-1)
    cover_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0002",
        value="0",
    )
    assert cover_actuator.position == 0
    await cover_actuator.set_position(120)
    cover_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0002",
        value="100",
    )
    assert cover_actuator.position == 100


@pytest.mark.asyncio
async def test_set_tilt_position(shutter_actuator):
    """Test to set a specific tilt of the shutter."""
    await shutter_actuator.set_tilt_position(50)
    shutter_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0003",
        value="50",
    )
    assert shutter_actuator.tilt_position == 50

    # Also checking lower and upper boundaries
    await shutter_actuator.set_tilt_position(-1)
    shutter_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0003",
        value="0",
    )
    assert shutter_actuator.tilt_position == 0
    await shutter_actuator.set_tilt_position(120)
    shutter_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB2AC253651",
        channel_id="ch0003",
        datapoint="idp0003",
        value="100",
    )
    assert shutter_actuator.tilt_position == 100


@pytest.mark.asyncio
async def test_refresh_state_from_output(cover_actuator):
    """Test the _refresh_state_from_output function."""
    # Check output that affects the state
    cover_actuator._refresh_state_from_output(
        output={"pairingID": 288, "value": "1"},
    )
    assert cover_actuator.state == 1

    # Check output that affects the forced position
    cover_actuator._refresh_state_from_output(output={"pairingID": 257, "value": "2"})
    assert cover_actuator.forced_position == 2

    # Check output that affects the position
    cover_actuator._refresh_state_from_output(output={"pairingID": 289, "value": "35"})
    assert cover_actuator.position == 35

    # Check output that affects the tilt
    cover_actuator._refresh_state_from_output(output={"pairingID": 290, "value": "45"})
    assert cover_actuator._tilt_position == 45

    # Check output that does NOT affects the RTC
    cover_actuator._refresh_state_from_output(
        output={"pairingID": 0, "value": "1"},
    )
    assert cover_actuator.position == 35
