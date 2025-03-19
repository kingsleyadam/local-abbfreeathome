"""Test class to test the virtual SwitchActuator device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.virtual.virtual_switch_actuator import (
    VirtualSwitchActuator,
    #    VirtualSwitchActuatorForcedPosition,
)


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def virtual_switch_actuator(mock_api):
    """Set up the switch instance for testing the virtual SwitchActuator device."""
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

    return VirtualSwitchActuator(
        device_id="60004F56EA24",
        device_name="Device Name",
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_initial_state(virtual_switch_actuator):
    """Test the intial state of the virtual switch."""
    assert virtual_switch_actuator.state is False


@pytest.mark.asyncio
async def test_turn_on(virtual_switch_actuator):
    """Test to turning on of the switch."""
    await virtual_switch_actuator.turn_on()
    assert virtual_switch_actuator.state is True
    virtual_switch_actuator._api.set_datapoint.assert_called_with(
        device_id="60004F56EA24",
        channel_id="ch0000",
        datapoint="odp0000",
        value="1",
    )


@pytest.mark.asyncio
async def test_turn_off(virtual_switch_actuator):
    """Test to turning off of the switch."""
    await virtual_switch_actuator.turn_off()
    assert virtual_switch_actuator.state is False
    virtual_switch_actuator._api.set_datapoint.assert_called_with(
        device_id="60004F56EA24",
        channel_id="ch0000",
        datapoint="odp0000",
        value="0",
    )


@pytest.mark.asyncio
async def test_set_forced_position(virtual_switch_actuator):
    """Test to set the forced option of the switch."""
    await virtual_switch_actuator.set_forced_position(
        VirtualSwitchActuatorForcedPosition.deactivated.name
    )
    assert (
        virtual_switch_actuator.forced_position
        == VirtualSwitchActuatorForcedPosition.deactivated.name
    )
    virtual_switch_actuator._api.set_datapoint.assert_called_with(
        device_id="60004F56EA24",
        channel_id="ch0000",
        datapoint="odp0001",
        value="0",
    )
    await virtual_switch_actuator.set_forced_position(
        VirtualSwitchActuatorForcedPosition.forced_off.name
    )
    assert (
        virtual_switch_actuator.forced_position
        == VirtualSwitchActuatorForcedPosition.forced_off.name
    )
    virtual_switch_actuator._api.set_datapoint.assert_called_with(
        device_id="60004F56EA24",
        channel_id="ch0000",
        datapoint="odp0001",
        value="5",
    )
    await virtual_switch_actuator.set_forced_position(
        VirtualSwitchActuatorForcedPosition.forced_on.name
    )
    assert (
        virtual_switch_actuator.forced_position
        == VirtualSwitchActuatorForcedPosition.forced_on.name
    )
    virtual_switch_actuator._api.set_datapoint.assert_called_with(
        device_id="60004F56EA24",
        channel_id="ch0000",
        datapoint="odp0001",
        value="4",
    )

    await virtual_switch_actuator.set_forced_position("INVALID")
    assert (
        virtual_switch_actuator.forced_position
        == VirtualSwitchActuatorForcedPosition.unknown.name
    )


@pytest.mark.asyncio
async def test_refresh_state(virtual_switch_actuator):
    """Test refreshing the state of the switch."""
    virtual_switch_actuator._api.get_datapoint.return_value = ["1"]
    await virtual_switch_actuator.refresh_state()
    assert virtual_switch_actuator.state is True
    virtual_switch_actuator._api.get_datapoint.assert_called_with(
        device_id="60004F56EA24",
        channel_id="ch0000",
        datapoint="idp0002",
    )


def test_update_device(virtual_switch_actuator):
    """Test updating the device state."""

    def test_callback():
        pass

    # Ensure callback is registered to test callback code.
    virtual_switch_actuator.register_callback(test_callback)

    virtual_switch_actuator.update_device("AL_SWITCH_ON_OFF/idp0000", "1")
    assert virtual_switch_actuator.state is True

    virtual_switch_actuator.update_device("AL_SWITCH_ON_OFF/idp0000", "0")
    assert virtual_switch_actuator.state is False

    # Test scenario where websocket sends update not relevant to the state.
    virtual_switch_actuator.update_device("AL_SWITCH_ON_OFF/idp0001", "1")
    assert virtual_switch_actuator.state is False
