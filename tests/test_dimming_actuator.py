"""Test class to test the DimmingActuator device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.dimming_actuator import (
    DimmingActuator,
    DimmingActuatorForcedPosition,
)


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
        "idp0004": {"pairingID": 3, "value": "0"},
    }
    outputs = {
        "odp0000": {"pairingID": 256, "value": "0"},
        "odp0001": {"pairingID": 272, "value": "50"},
        "odp0002": {"pairingID": 273, "value": "0"},
        "odp0003": {"pairingID": 257, "value": "0"},
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
    """Test to set brightness off the DimmingActuator."""
    await dimming_actuator.set_brightness(50)
    assert dimming_actuator.brightness == 50
    await dimming_actuator.set_brightness(-1)
    assert dimming_actuator.brightness == 1
    await dimming_actuator.set_brightness(110)
    assert dimming_actuator.brightness == 100


@pytest.mark.asyncio
async def test_set_forced(dimming_actuator):
    """Test to set the forced option of the DimmingActuator."""
    await dimming_actuator.set_forced_position(
        DimmingActuatorForcedPosition.deactivated.name
    )
    assert (
        dimming_actuator.forced_position
        == DimmingActuatorForcedPosition.deactivated.name
    )
    dimming_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB70139AF8A",
        channel_id="ch0000",
        datapoint="idp0004",
        value="0",
    )
    await dimming_actuator.set_forced_position(
        DimmingActuatorForcedPosition.forced_off.name
    )
    assert (
        dimming_actuator.forced_position
        == DimmingActuatorForcedPosition.forced_off.name
    )
    dimming_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB70139AF8A",
        channel_id="ch0000",
        datapoint="idp0004",
        value="2",
    )
    await dimming_actuator.set_forced_position(
        DimmingActuatorForcedPosition.forced_on.name
    )
    assert (
        dimming_actuator.forced_position == DimmingActuatorForcedPosition.forced_on.name
    )
    dimming_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB70139AF8A",
        channel_id="ch0000",
        datapoint="idp0004",
        value="3",
    )

    await dimming_actuator.set_forced_position("INVALID")
    assert (
        dimming_actuator.forced_position == DimmingActuatorForcedPosition.unknown.name
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
        datapoint="odp0001",
    )


def test_refresh_state_from_output(dimming_actuator):
    """Test the _refresh_state_from_output function."""
    # Check output that affects the state.
    dimming_actuator._refresh_state_from_output(
        output={"pairingID": 256, "value": "1"},
    )
    assert dimming_actuator.state is True

    # Check output that affects the brightness
    dimming_actuator._refresh_state_from_output(
        output={"pairingID": 272, "value": 75},
    )
    assert dimming_actuator.brightness == 75

    # Check output that affects the force-option
    dimming_actuator._refresh_state_from_output(
        output={
            "pairingID": 257,
            "value": DimmingActuatorForcedPosition.forced_on.value,
        },
    )
    assert (
        dimming_actuator.forced_position == DimmingActuatorForcedPosition.forced_on.name
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
