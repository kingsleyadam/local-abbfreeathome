"""Test class to test the DesDoorOpenerActuator channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.des_door_opener_actuator import DesDoorOpenerActuator
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
def des_door_opener_actuator(mock_api, mock_device):
    """Set up the instance for testing the DesDoorOpenerActuator channel."""
    inputs = {
        "idp0000": {"pairingID": 2, "value": "0"},
    }
    outputs = {
        "odp0000": {"pairingID": 256, "value": "0"},
        "odp0001": {"pairingID": 0, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "0007EE9503A4"

    mock_device.api = mock_api
    return DesDoorOpenerActuator(
        device=mock_device,
        channel_id="ch0040",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_initial_state(des_door_opener_actuator):
    """Test the intial state of the DesDoorOpenerActuator."""
    assert des_door_opener_actuator.state is False


@pytest.mark.asyncio
async def test_lock(des_door_opener_actuator):
    """Test to lock."""
    await des_door_opener_actuator.lock()
    assert des_door_opener_actuator.state is False
    des_door_opener_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="0007EE9503A4",
        channel_id="ch0040",
        datapoint="idp0000",
        value="0",
    )


@pytest.mark.asyncio
async def test_unlock(des_door_opener_actuator):
    """Test to unlock."""
    await des_door_opener_actuator.unlock()
    assert des_door_opener_actuator.state is True
    des_door_opener_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="0007EE9503A4",
        channel_id="ch0040",
        datapoint="idp0000",
        value="1",
    )


@pytest.mark.asyncio
async def test_refresh_state(des_door_opener_actuator):
    """Test refreshing the state of the DesDoorOpenerActuator."""
    des_door_opener_actuator.device.api.get_datapoint.return_value = ["1"]
    await des_door_opener_actuator.refresh_state()
    assert des_door_opener_actuator.state is True
    des_door_opener_actuator.device.api.get_datapoint.assert_called_with(
        device_serial="0007EE9503A4",
        channel_id="ch0040",
        datapoint="odp0000",
    )
