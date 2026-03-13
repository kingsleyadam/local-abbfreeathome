"""Test class to test the MWireSwitchActuator channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.switch_actuator import MWireSwitchActuator
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
def mwire_switch_actuator(mock_api, mock_device):
    """Set up the switch instance for testing the MWireSwitchActuator channel."""
    inputs = {
        "idp0000": {"pairingID": 419, "value": ""},
        "idp0001": {"pairingID": 18, "value": "0"},
        "idp0002": {"pairingID": 359, "value": ""},
        "idp0003": {"pairingID": 420, "value": ""},
    }
    outputs = {
        "odp0000": {"pairingID": 419, "value": "1"},
        "odp0001": {"pairingID": 420, "value": ""},
        "odp0002": {"pairingID": 417, "value": "65535"},
        "odp0003": {"pairingID": 360, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "ABB703034BE8"
    mock_device.api = mock_api
    return MWireSwitchActuator(
        device=mock_device,
        channel_id="ch0010",
        channel_name="BJ_Taster_Kamin",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_initial_state(mwire_switch_actuator):
    """Test the initial state of the switch."""
    assert mwire_switch_actuator.state is True


@pytest.mark.asyncio
async def test_turn_on(mwire_switch_actuator):
    """Test turning on the switch."""
    await mwire_switch_actuator.turn_on()
    assert mwire_switch_actuator.state is True
    mwire_switch_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB703034BE8",
        channel_id="ch0010",
        datapoint="idp0000",
        value="1",
    )


@pytest.mark.asyncio
async def test_turn_off(mwire_switch_actuator):
    """Test turning off the switch."""
    await mwire_switch_actuator.turn_off()
    assert mwire_switch_actuator.state is False
    mwire_switch_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB703034BE8",
        channel_id="ch0010",
        datapoint="idp0000",
        value="0",
    )


@pytest.mark.asyncio
async def test_refresh_state(mwire_switch_actuator):
    """Test refreshing the state of the switch."""
    mwire_switch_actuator.device.api.get_datapoint.return_value = ["1"]
    await mwire_switch_actuator.refresh_state()
    assert mwire_switch_actuator.state is True
    mwire_switch_actuator.device.api.get_datapoint.assert_called_with(
        device_serial="ABB703034BE8",
        channel_id="ch0010",
        datapoint="odp0000",
    )


def test_update_channel(mwire_switch_actuator):
    """Test updating the channel state."""

    def test_callback():
        pass

    mwire_switch_actuator.register_callback(
        callback_attribute="state", callback=test_callback
    )

    mwire_switch_actuator.update_channel("AL_MWIRE_SWITCH_ON_OFF/odp0000", "1")
    assert mwire_switch_actuator.state is True

    mwire_switch_actuator.update_channel("AL_MWIRE_SWITCH_ON_OFF/odp0000", "0")
    assert mwire_switch_actuator.state is False

    # Test scenario where websocket sends update not relevant to the state.
    mwire_switch_actuator.update_channel("AL_MWIRE_SWITCH_ON_OFF/odp0002", "1")
    assert mwire_switch_actuator.state is False
