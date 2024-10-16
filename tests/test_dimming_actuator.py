"""Test class to test the DimmingActuator device."""

from unittest.mock import AsyncMock

import pytest

from abbfreeathome.api import FreeAtHomeApi
from abbfreeathome.devices.dimming_actuator import DimmingActuator


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def dimming_actuator(mock_api):
    """Set up the dimming instance for testing the DimmingActuator device."""
    inputs = {
        "idp0000": {"pairingID": 1, "value": "0"},
        "idp0002": {"pairingID": 17, "value": "50"},
    }
    outputs = {
        "odp0000": {"pairingID": 256, "value": "0"},
        "odp0001": {"pairingID": 272, "value": "50"},
    }
    parameters = {}

    return DimmingActuator(
        device_id="ABB70139AF8A",
        device_name="Device Name",
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_initial_state(dimming_actuator):
    """Test the intial state of the DimmingActuator."""
    assert dimming_actuator.state is False


@pytest.mark.asyncio
async def test_turn_on(dimming_actuator):
    """Test to turning on the DimmingActuator."""
    await dimming_actuator.turn_on()
    assert dimming_actuator.state is True
    dimming_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB70139AF8A",
        channel_id="ch0000",
        datapoint="idp0000",
        value="1",
    )


@pytest.mark.asyncio
async def test_turn_off(dimming_actuator):
    """Test to turning off the DimmingActuator."""
    await dimming_actuator.turn_off()
    assert dimming_actuator.state is False
    dimming_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB70139AF8A",
        channel_id="ch0000",
        datapoint="idp0000",
        value="0",
    )


@pytest.mark.asyncio
async def test_set_brightness(dimming_actuator):
    """Test to set brightness of the DimmingActuator."""
    await dimming_actuator.set_brightness(100)
    assert dimming_actuator.brightness == 100
    dimming_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB70139AF8A",
        channel_id="ch0000",
        datapoint="idp0002",
        value="100",
    )
    await dimming_actuator.set_brightness(-1)
    assert dimming_actuator.brightness == 1
    dimming_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB70139Af8A",
        channel_id="ch0000",
        datapoint="idp0002",
        value="1",
    )
    await dimming_actuator.set_brightness(110)
    assert dimming_actuator.brightness == 100
    dimming_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB70139Af8A",
        channel_id="ch0000",
        datapoint="idp0002",
        value="100",
    )


@pytest.mark.asyncio
async def test_refresh_state(dimming_actuator):
    """Test refreshing the state of the DimmingActuator."""
    dimming_actuator._api.get_datapoint.return_value = ["1"]
    await dimming_actuator.refresh_state()
    assert dimming_actuator.state is True
    dimming_actuator._api.get_datapoint.assert_called_with(
        device_id="ABB70139AF8A",
        channel_id="ch0000",
        datapoint="odp0000",
    )


def test_update_device(dimming_actuator):
    """Test updating the device state."""

    def test_callback():
        pass

    # Ensure callback is registered to test callback code.
    dimming_actuator.register_callback(test_callback)

    dimming_actuator.update_device("AL_INFO_ON_OFF/odp0000", "1")
    assert dimming_actuator.state is True

    dimming_actuator.update_device("AL_INFO_ON_OFF/odp0000", "0")
    assert dimming_actuator.state is False

    # Test scenario where websocket sends update not relevant to the state.
    dimming_actuator.update_device("AL_INFO_ON_OFF/odp0001", "1")
    assert dimming_actuator.state is False

    dimming_actuator.update_device("AL_INFO_ON_OFF/idp0000", "1")
