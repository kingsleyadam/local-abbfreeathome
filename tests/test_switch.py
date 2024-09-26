"""Test class to test the Switch device."""

from unittest.mock import AsyncMock

import pytest

from abbfreeathome.api import FreeAtHomeApi
from abbfreeathome.devices.switch import Switch


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def switch(mock_api):
    """Set up the switch instance for testing the Switch device."""
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
    }
    parameters = {}

    return Switch(
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
async def test_initial_state(switch):
    """Test the intial state of the switch."""
    assert switch.state is False


@pytest.mark.asyncio
async def test_turn_on(switch):
    """Test to turning on of the switch."""
    await switch.turn_on()
    assert switch.state is True
    switch._api.set_datapoint.assert_called_with(
        device_id="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="idp0000",
        value="1",
    )


@pytest.mark.asyncio
async def test_turn_off(switch):
    """Test to turning off of the switch."""
    await switch.turn_off()
    assert switch.state is False
    switch._api.set_datapoint.assert_called_with(
        device_id="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="idp0000",
        value="0",
    )


@pytest.mark.asyncio
async def test_refresh_state(switch):
    """Test refreshing the state of the switch."""
    switch._api.get_datapoint.return_value = ["1"]
    await switch.refresh_state()
    assert switch.state is True
    switch._api.get_datapoint.assert_called_with(
        device_id="ABB7F500E17A",
        channel_id="ch0003",
        datapoint="odp0000",
    )


def test_update_device(switch):
    """Test updating the device state."""
    switch.update_device("AL_INFO_ON_OFF/odp0000", "1")
    assert switch.state is True

    switch.update_device("AL_INFO_ON_OFF/odp0000", "0")
    assert switch.state is False

    switch.update_device("AL_INFO_ON_OFF/idp0000", "1")
