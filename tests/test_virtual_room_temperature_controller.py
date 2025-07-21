"""Test class to test the virtual RoomTemperatureController channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.virtual.virtual_room_temperature_controller import (
    VirtualRoomTemperatureController,
)
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
def virtual_room_temperature_controller(mock_api, mock_device):
    """Set up the controller instance for testing the virtual RoomTemperatureController channel."""  # noqa: E501
    inputs = {
        "idp0011": {"pairingID": 58, "value": ""},
        "idp0012": {"pairingID": 66, "value": ""},
        "idp0014": {"pairingID": 4, "value": ""},
        "idp0016": {"pairingID": 320, "value": ""},
    }
    outputs = {
        "odp0006": {"pairingID": 51, "value": "0"},
        "odp0008": {"pairingID": 56, "value": "0"},
        "odp0009": {"pairingID": 54, "value": "0"},
        "odp0010": {"pairingID": 304, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "60002AF0162C"

    mock_device.api = mock_api
    return VirtualRoomTemperatureController(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_initial_state(virtual_room_temperature_controller):
    """Test the intial state of the virtual controller."""
    assert virtual_room_temperature_controller.state is False


@pytest.mark.asyncio
async def test_turn_on(virtual_room_temperature_controller):
    """Test to turning on of the controller."""
    await virtual_room_temperature_controller.turn_on()
    assert virtual_room_temperature_controller.state is True
    virtual_room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="60002AF0162C",
        channel_id="ch0000",
        datapoint="odp0008",
        value="1",
    )


@pytest.mark.asyncio
async def test_turn_off(virtual_room_temperature_controller):
    """Test to turning off of the switch."""
    await virtual_room_temperature_controller.turn_off()
    assert virtual_room_temperature_controller.state is False
    virtual_room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="60002AF0162C",
        channel_id="ch0000",
        datapoint="odp0008",
        value="0",
    )


@pytest.mark.asyncio
async def test_turn_on_eco_mode(virtual_room_temperature_controller):
    """Test to turning on the eco-mode of the controller."""
    await virtual_room_temperature_controller.turn_on_eco_mode()
    assert virtual_room_temperature_controller.eco_mode is True
    virtual_room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="60002AF0162C",
        channel_id="ch0000",
        datapoint="odp0009",
        value="68",
    )


@pytest.mark.asyncio
async def test_turn_off_eco_mode(virtual_room_temperature_controller):
    """Test to turning off the eco-mode of the switch."""
    await virtual_room_temperature_controller.turn_off_eco_mode()
    assert virtual_room_temperature_controller.eco_mode is False
    virtual_room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="60002AF0162C",
        channel_id="ch0000",
        datapoint="odp0009",
        value="65",
    )


@pytest.mark.asyncio
async def test_set_target_temperature(virtual_room_temperature_controller):
    """Test to set target temperature of the sensor."""
    await virtual_room_temperature_controller.set_target_temperature(20)
    virtual_room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="60002AF0162C",
        channel_id="ch0000",
        datapoint="odp0006",
        value="20",
    )
    assert virtual_room_temperature_controller.target_temperature == 20
    # test lower boundary
    await virtual_room_temperature_controller.set_target_temperature(5)
    virtual_room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="60002AF0162C",
        channel_id="ch0000",
        datapoint="odp0006",
        value="7",
    )
    assert virtual_room_temperature_controller.target_temperature == 7
    # test upper boundary
    await virtual_room_temperature_controller.set_target_temperature(50)
    virtual_room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="60002AF0162C",
        channel_id="ch0000",
        datapoint="odp0006",
        value="35",
    )
    assert virtual_room_temperature_controller.target_temperature == 35


@pytest.mark.asyncio
async def test_set_current_temperature(virtual_room_temperature_controller):
    """Test to set current temperature of the sensor."""
    await virtual_room_temperature_controller.set_current_temperature(20)
    virtual_room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="60002AF0162C",
        channel_id="ch0000",
        datapoint="odp0010",
        value="20",
    )
    assert virtual_room_temperature_controller.current_temperature == 20


@pytest.mark.asyncio
async def test_refresh_state(virtual_room_temperature_controller):
    """Test refreshing the state of the controller."""
    virtual_room_temperature_controller.device.api.get_datapoint.return_value = ["20"]
    await virtual_room_temperature_controller.refresh_state()
    assert virtual_room_temperature_controller.current_temperature == 20
    virtual_room_temperature_controller.device.api.get_datapoint.assert_called_with(
        device_serial="60002AF0162C",
        channel_id="ch0000",
        datapoint="odp0010",
    )


def test_update_channel(virtual_room_temperature_controller):
    """Test updating the channel state."""

    def test_callback():
        pass

    # Ensure callback is registered to test callback code.
    virtual_room_temperature_controller.register_callback(
        callback_attribute="state", callback=test_callback
    )
    virtual_room_temperature_controller.register_callback(
        callback_attribute="requested_state", callback=test_callback
    )
    virtual_room_temperature_controller.register_callback(
        callback_attribute="current_temperature", callback=test_callback
    )
    virtual_room_temperature_controller.register_callback(
        callback_attribute="target_temperature", callback=test_callback
    )
    virtual_room_temperature_controller.register_callback(
        callback_attribute="requested_target_temperature", callback=test_callback
    )
    virtual_room_temperature_controller.register_callback(
        callback_attribute="eco_mode", callback=test_callback
    )
    virtual_room_temperature_controller.register_callback(
        callback_attribute="requested_eco_mode", callback=test_callback
    )

    virtual_room_temperature_controller.update_channel("AL_SWITCH_ON_OFF/odp0008", "1")
    assert virtual_room_temperature_controller.state is True

    virtual_room_temperature_controller.update_channel("AL_SWITCH_ON_OFF/odp0008", "0")
    assert virtual_room_temperature_controller.state is False

    virtual_room_temperature_controller.update_channel("AL_SWITCH_ON_OFF/idp0012", "1")
    assert virtual_room_temperature_controller.requested_state is True

    virtual_room_temperature_controller.update_channel("AL_SWITCH_ON_OFF/idp0012", "0")
    assert virtual_room_temperature_controller.requested_state is False

    virtual_room_temperature_controller.update_channel("AL_SWITCH_ON_OFF/odp0009", "68")
    assert virtual_room_temperature_controller.eco_mode is True

    virtual_room_temperature_controller.update_channel("AL_SWITCH_ON_OFF/odp0009", "65")
    assert virtual_room_temperature_controller.eco_mode is False

    virtual_room_temperature_controller.update_channel("AL_SWITCH_ON_OFF/idp0011", "1")
    assert virtual_room_temperature_controller.requested_eco_mode is True

    virtual_room_temperature_controller.update_channel("AL_SWITCH_ON_OFF/idp0011", "0")
    assert virtual_room_temperature_controller.requested_eco_mode is False

    virtual_room_temperature_controller.update_channel("AL_SWITCH_ON_OFF/odp0006", "20")
    assert virtual_room_temperature_controller.target_temperature == 20

    virtual_room_temperature_controller.update_channel("AL_SWITCH_ON_OFF/idp0016", "20")
    assert virtual_room_temperature_controller.requested_target_temperature == 20

    virtual_room_temperature_controller.update_channel("AL_SWITCH_ON_OFF/odp0010", "20")
    assert virtual_room_temperature_controller.current_temperature == 20

    # Test scenario where websocket sends update not relevant to the state.
    virtual_room_temperature_controller.update_channel("AL_SWITCH_ON_OFF/idp0014", "1")
    assert virtual_room_temperature_controller.state is False
