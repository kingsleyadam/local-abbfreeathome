"""Test class to test the SwitchActuator channel."""

from unittest.mock import AsyncMock, MagicMock, call

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.movement_detector import (
    BlockableMovementDetector,
    MovementDetector,
)
from src.abbfreeathome.device import Device


def get_movement_detector(type: str, mock_api, mock_device):
    """Get the MovementDetector class to be tested against."""
    inputs = {
        "idp0000": {"pairingID": 256, "value": "0"},
        "idp0004": {"pairingID": 359, "value": "0"},
    }
    outputs = {
        "odp0000": {"pairingID": 6, "value": "0"},
        "odp0002": {"pairingID": 1027, "value": "1.6"},
        "odp0005": {"pairingID": 360, "value": "0"},
    }
    parameters = {"par0034": "1", "par00d5": "100"}

    # If it's outdoor it won't have brightness
    if type == "outdoor":
        outputs.pop("odp0002")

    # If it's not blockable it won't have blocking feature
    if type != "blockable":
        inputs.pop("idp0004")
        outputs.pop("odp0005")

    mock_device.device_serial = "ABB7F500E17A"
    mock_device.api = mock_api

    if type == "blockable":
        return BlockableMovementDetector(
            device=mock_device,
            channel_id="ch0003",
            channel_name="Channel Name",
            inputs=inputs,
            outputs=outputs,
            parameters=parameters,
        )
    return MovementDetector(
        device=mock_device,
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.fixture
def mock_api():
    """Create a mock api."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def mock_device():
    """Create a mock device."""
    return MagicMock(spec=Device)


@pytest.fixture
def indoor_movement_detector(mock_api, mock_device):
    """Create an instance for testing the indoor MovementDetector."""
    return get_movement_detector("indoor", mock_api, mock_device)


@pytest.fixture
def outdoor_movement_detector(mock_api, mock_device):
    """Create an instance for testing the outdoor MovementDetector."""
    return get_movement_detector("outdoor", mock_api, mock_device)


@pytest.fixture
def blockable_movement_detector(mock_api, mock_device):
    """Create an instance for testing the BlockableMovementDetector."""
    return get_movement_detector("blockable", mock_api, mock_device)


@pytest.mark.asyncio
async def test_initial_state_indoor(indoor_movement_detector):
    """Test the intial state (indoor)."""
    assert indoor_movement_detector.state is False
    assert indoor_movement_detector.brightness == 1.6


@pytest.mark.asyncio
async def test_initial_state_outdoor(outdoor_movement_detector):
    """Test the intial state (outdoor)."""
    assert outdoor_movement_detector.state is False
    assert outdoor_movement_detector.brightness is None


@pytest.mark.asyncio
async def test_initial_state_blockable(blockable_movement_detector):
    """Test the intial state (blockable)."""
    assert blockable_movement_detector.state is False
    assert blockable_movement_detector.brightness == 1.6
    assert blockable_movement_detector.blocked is False


@pytest.mark.asyncio
async def test_refresh_state(indoor_movement_detector):
    """Test refreshing the state."""
    indoor_movement_detector.device.api.get_datapoint.side_effect = [
        ["1"],
        ["42.1"],
    ]
    await indoor_movement_detector.refresh_state()
    assert indoor_movement_detector.state is True
    assert indoor_movement_detector.brightness == 42.1
    _expected_calls = [
        call(device_serial="ABB7F500E17A", channel_id="ch0003", datapoint="odp0000"),
        call(device_serial="ABB7F500E17A", channel_id="ch0003", datapoint="odp0002"),
    ]
    indoor_movement_detector.device.api.get_datapoint.assert_has_calls(_expected_calls)


@pytest.mark.asyncio
async def test_refresh_state_blockable(blockable_movement_detector):
    """Test refreshing the state (blockable)."""
    blockable_movement_detector.device.api.get_datapoint.side_effect = [
        ["1"],
        ["42.1"],
        ["1"],
    ]
    await blockable_movement_detector.refresh_state()
    assert blockable_movement_detector.state is True
    assert blockable_movement_detector.brightness == 42.1
    assert blockable_movement_detector.blocked is True
    _expected_calls = [
        call(device_serial="ABB7F500E17A", channel_id="ch0003", datapoint="odp0000"),
        call(device_serial="ABB7F500E17A", channel_id="ch0003", datapoint="odp0002"),
        call(device_serial="ABB7F500E17A", channel_id="ch0003", datapoint="odp0005"),
    ]
    blockable_movement_detector.device.api.get_datapoint.assert_has_calls(
        _expected_calls
    )


def test_refresh_state_from_datapoint(indoor_movement_detector):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the state.
    indoor_movement_detector._refresh_state_from_datapoint(
        datapoint={"pairingID": 6, "value": "1"},
    )
    assert indoor_movement_detector.state is True
    assert indoor_movement_detector.brightness == 1.6

    # Check output that affects the state.
    indoor_movement_detector._refresh_state_from_datapoint(
        datapoint={"pairingID": 1027, "value": "52.3"},
    )
    assert indoor_movement_detector.state is True
    assert indoor_movement_detector.brightness == 52.3

    # Check output that does NOT affect the state.
    indoor_movement_detector._refresh_state_from_datapoint(
        datapoint={"pairingID": 12, "value": "0"},
    )
    assert indoor_movement_detector.state is True
    assert indoor_movement_detector.brightness == 52.3


def test_refresh_state_from_datapoint_blockable(blockable_movement_detector):
    """Test the _refresh_state_from_datapoint function (blockable)."""
    # Check output that affects the state.
    blockable_movement_detector._refresh_state_from_datapoint(
        datapoint={"pairingID": 6, "value": "1"},
    )
    assert blockable_movement_detector.state is True
    assert blockable_movement_detector.brightness == 1.6
    assert blockable_movement_detector.blocked is False

    # Check output that affects the state.
    blockable_movement_detector._refresh_state_from_datapoint(
        datapoint={"pairingID": 1027, "value": "52.3"},
    )
    assert blockable_movement_detector.state is True
    assert blockable_movement_detector.brightness == 52.3
    assert blockable_movement_detector.blocked is False

    # Check output that affects the state.
    blockable_movement_detector._refresh_state_from_datapoint(
        datapoint={"pairingID": 360, "value": "1"},
    )
    assert blockable_movement_detector.state is True
    assert blockable_movement_detector.brightness == 52.3
    assert blockable_movement_detector.blocked is True

    # Check output that does NOT affect the state.
    blockable_movement_detector._refresh_state_from_datapoint(
        datapoint={"pairingID": 12, "value": "0"},
    )
    assert blockable_movement_detector.state is True
    assert blockable_movement_detector.brightness == 52.3
    assert blockable_movement_detector.blocked is True


@pytest.mark.asyncio
async def test_block(blockable_movement_detector):
    """Test for blocking the sensor."""
    await blockable_movement_detector.turn_on_blocked()
    assert blockable_movement_detector.blocked is True
    blockable_movement_detector.device.api.set_datapoint.assert_called_with(
        device_serial="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="idp0004",
        value="1",
    )


@pytest.mark.asyncio
async def test_unblock(blockable_movement_detector):
    """Test for unblocking the sensor."""
    await blockable_movement_detector.turn_off_blocked()
    assert blockable_movement_detector.blocked is False
    blockable_movement_detector.device.api.set_datapoint.assert_called_with(
        device_serial="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="idp0004",
        value="0",
    )
