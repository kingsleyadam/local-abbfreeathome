"""Test class to test the SwitchActuator device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.switch_actuator import (
    SwitchActuator,
    SwitchActuatorForcedPosition,
)


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def switch_actuator(mock_api):
    """Set up the switch instance for testing the SwitchActuator device."""
    inputs = {
        "idp0000": {"pairingID": 1, "value": "0"},
        "idp0001": {"pairingID": 2, "value": "0"},
        "idp0002": {"pairingID": 3, "value": "0"},
        "idp0003": {"pairingID": 4, "value": "1"},
        "idp0004": {"pairingID": 6, "value": "0"},
    }
    outputs = {
        "odp0000": {"pairingID": 256, "value": "0"},
        "odp0001": {"pairingID": 257, "value": "0"},
        "odp0004": {"pairingID": 273, "value": "0"},
    }
    parameters = {}

    return SwitchActuator(
        device_id="ABB7F500E17A",
        device_name="Device Name",
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_initial_state(switch_actuator):
    """Test the intial state of the switch."""
    assert switch_actuator.state is False


@pytest.mark.asyncio
async def test_turn_on(switch_actuator):
    """Test to turning on of the switch."""
    await switch_actuator.turn_on()
    assert switch_actuator.state is True
    switch_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="idp0000",
        value="1",
    )


@pytest.mark.asyncio
async def test_turn_off(switch_actuator):
    """Test to turning off of the switch."""
    await switch_actuator.turn_off()
    assert switch_actuator.state is False
    switch_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="idp0000",
        value="0",
    )


@pytest.mark.asyncio
async def test_set_forced(switch_actuator):
    """Test to set the forced option of the switch."""
    await switch_actuator.set_forced_position(
        SwitchActuatorForcedPosition.deactivated.name
    )
    assert (
        switch_actuator.forced_position == SwitchActuatorForcedPosition.deactivated.name
    )
    switch_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="idp0002",
        value="0",
    )
    await switch_actuator.set_forced_position(
        SwitchActuatorForcedPosition.forced_off.name
    )
    assert (
        switch_actuator.forced_position == SwitchActuatorForcedPosition.forced_off.name
    )
    switch_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="idp0002",
        value="2",
    )
    await switch_actuator.set_forced_position(
        SwitchActuatorForcedPosition.forced_on.name
    )
    assert (
        switch_actuator.forced_position == SwitchActuatorForcedPosition.forced_on.name
    )
    switch_actuator._api.set_datapoint.assert_called_with(
        device_id="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="idp0002",
        value="3",
    )

    await switch_actuator.set_forced_position("INVALID")
    assert switch_actuator.forced_position == SwitchActuatorForcedPosition.unknown.name


@pytest.mark.asyncio
async def test_refresh_state(switch_actuator):
    """Test refreshing the state of the switch."""
    switch_actuator._api.get_datapoint.return_value = ["1"]
    await switch_actuator.refresh_state()
    assert switch_actuator.state is True
    switch_actuator._api.get_datapoint.assert_called_with(
        device_id="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="odp0000",
    )


def test_update_device(switch_actuator):
    """Test updating the device state."""

    def test_callback():
        pass

    # Ensure callback is registered to test callback code.
    switch_actuator.register_callback(
        callback_attribute="state", callback=test_callback
    )

    switch_actuator.update_device("AL_INFO_ON_OFF/odp0000", "1")
    assert switch_actuator.state is True

    switch_actuator.update_device("AL_INFO_ON_OFF/odp0000", "0")
    assert switch_actuator.state is False

    # Test scenario where websocket sends update not relevant to the state.
    switch_actuator.update_device("AL_INFO_ON_OFF/odp0004", "1")
    assert switch_actuator.state is False
