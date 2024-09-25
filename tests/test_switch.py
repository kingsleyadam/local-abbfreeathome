"""Test class to test the Switch device."""

from unittest.mock import AsyncMock

import pytest

from abbfreeathome.api import FreeAtHomeApi
from abbfreeathome.bin.pairing_id import PairingId
from abbfreeathome.devices.switch import Switch


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def switch(mock_api):
    """Set up the switch instance for testing the Switch device."""
    inputs = {
        "input1": {"pairingID": 1, "value": "0"},
        "input2": {"pairingID": 2, "value": "0"},
    }
    outputs = {
        "output1": {
            "pairingID": PairingId.AL_INFO_ON_OFF.value,
            "value": "0",
        }
    }
    parameters = {}

    return Switch(
        device_id="device123",
        device_name="Device Name",
        channel_id="channel123",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_initial_state(switch):
    """Test the intial state of the switch."""
    assert switch.state is False


@pytest.mark.asyncio
async def test_turn_on(switch):
    """Test to turning on of the switch."""
    await switch.turn_on()
    assert switch.state is True
    switch._api.set_datapoint.assert_called_with(  # noqa: SLF001
        device_id="device123",
        channel_id="channel123",
        datapoint="input1",
        value="1",
    )


@pytest.mark.asyncio
async def test_turn_off(switch):
    """Test to turning off of the switch."""
    await switch.turn_off()
    assert switch.state is False
    switch._api.set_datapoint.assert_called_with(  # noqa: SLF001
        device_id="device123",
        channel_id="channel123",
        datapoint="input1",
        value="0",
    )


@pytest.mark.asyncio
async def test_refresh_state(switch):
    """Test refreshing the state of the switch."""
    switch._api.get_datapoint.return_value = ["1"]  # noqa: SLF001
    await switch.refresh_state()
    assert switch.state is True
    switch._api.get_datapoint.assert_called_with(  # noqa: SLF001
        device_id="device123",
        channel_id="channel123",
        datapoint="output1",
    )


def test_update_device(switch):
    """Test updating the device state."""
    switch.update_device("AL_INFO_ON_OFF/output1", "1")
    assert switch.state is True

    switch.update_device("AL_INFO_ON_OFF/output1", "0")
    assert switch.state is False

    switch.update_device("AL_INFO_ON_OFF/input1", "1")
