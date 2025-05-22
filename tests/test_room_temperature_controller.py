"""Test class to test the RoomTemperatureController device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.room_temperature_controller import (
    RoomTemperatureController,
)


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def room_temperature_controller(mock_api):
    """Set up the RTC instance for testing the RTC device."""
    inputs = {
        "idp0011": {"pairingID": 58, "value": "0"},
        "idp0012": {"pairingID": 66, "value": "1"},
        "idp0014": {"pairingID": 4, "value": "0"},
        "idp0016": {"pairingID": 320, "value": "0"},
    }
    outputs = {
        "odp0000": {"pairingID": 48, "value": "0"},
        "odp0001": {"pairingID": 50, "value": "0"},
        "odp0006": {"pairingID": 51, "value": "20"},
        "odp0008": {"pairingID": 56, "value": "1"},
        "odp0009": {"pairingID": 54, "value": "65"},
        "odp0010": {"pairingID": 304, "value": "21.34"},
    }
    parameters = {}

    return RoomTemperatureController(
        device_id="ABB700D72CC9",
        device_name="Device Name",
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_initial_state(room_temperature_controller):
    """Test the intial state of the RTC."""
    assert room_temperature_controller.state is True


@pytest.mark.asyncio
async def test_turn_on(room_temperature_controller):
    """Test to turning on the RTC."""
    await room_temperature_controller.turn_on()
    assert room_temperature_controller.state is True
    room_temperature_controller._api.set_datapoint.assert_called_with(
        device_id="ABB700D72CC9",
        channel_id="ch0000",
        datapoint="idp0012",
        value="1",
    )


@pytest.mark.asyncio
async def test_turn_off(room_temperature_controller):
    """Test to turning off the RTC."""
    await room_temperature_controller.turn_off()
    assert room_temperature_controller.state is False
    room_temperature_controller._api.set_datapoint.assert_called_with(
        device_id="ABB700D72CC9",
        channel_id="ch0000",
        datapoint="idp0012",
        value="0",
    )


@pytest.mark.asyncio
async def test_eco_on(room_temperature_controller):
    """Test to turning on the eco-mode."""
    await room_temperature_controller.eco_on()
    assert room_temperature_controller.eco_mode is True
    room_temperature_controller._api.set_datapoint.assert_called_with(
        device_id="ABB700D72CC9",
        channel_id="ch0000",
        datapoint="idp0011",
        value="1",
    )


@pytest.mark.asyncio
async def test_eco_off(room_temperature_controller):
    """Test to turning off the eco-mode."""
    await room_temperature_controller.eco_off()
    assert room_temperature_controller.eco_mode is False
    room_temperature_controller._api.set_datapoint.assert_called_with(
        device_id="ABB700D72CC9",
        channel_id="ch0000",
        datapoint="idp0011",
        value="0",
    )


@pytest.mark.asyncio
async def test_set_temperature(room_temperature_controller):
    """Test to set the target temperatuer of the RTC."""
    await room_temperature_controller.set_temperature(30)
    assert room_temperature_controller.target_temperature == 30
    room_temperature_controller._api.set_datapoint.assert_called_with(
        device_id="ABB700D72CC9", channel_id="ch0000", datapoint="idp0016", value="30"
    )
    # Also checking lower and upper boundaries
    await room_temperature_controller.set_temperature(0)
    assert room_temperature_controller.target_temperature == 7
    room_temperature_controller._api.set_datapoint.assert_called_with(
        device_id="ABB700D72CC9", channel_id="ch0000", datapoint="idp0016", value="7"
    )
    await room_temperature_controller.set_temperature(50)
    assert room_temperature_controller.target_temperature == 35
    room_temperature_controller._api.set_datapoint.assert_called_with(
        device_id="ABB700D72CC9", channel_id="ch0000", datapoint="idp0016", value="35"
    )


@pytest.mark.asyncio
async def test_refresh_state(room_temperature_controller):
    """Test refreshing state of the RTC."""
    room_temperature_controller._api.get_datapoint.return_value = ["1"]
    await room_temperature_controller.refresh_state()
    assert room_temperature_controller.state is True
    room_temperature_controller._api.get_datapoint.assert_called_with(
        device_id="ABB700D72CC9",
        channel_id="ch0000",
        datapoint="odp0008",
    )


@pytest.mark.asyncio
async def test_refresh_state_from_datapoint(
    room_temperature_controller,
):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the target_temperature
    room_temperature_controller._refresh_state_from_datapoint(
        datapoint={"pairingID": 51, "value": "25"},
    )
    assert room_temperature_controller.target_temperature == 25

    # Check output that affects the state
    room_temperature_controller._refresh_state_from_datapoint(
        datapoint={"pairingID": 56, "value": "0"},
    )
    assert room_temperature_controller.state is False

    # Check output that affects state_indication and eco_mode
    room_temperature_controller._refresh_state_from_datapoint(
        datapoint={"pairingID": 54, "value": "68"}
    )
    assert room_temperature_controller.state_indication == 68
    assert room_temperature_controller.eco_mode is True

    # Check output that affects the current temperature
    room_temperature_controller._refresh_state_from_datapoint(
        datapoint={"pairingID": 304, "value": "22.56"}
    )
    assert room_temperature_controller.current_temperature == 22.56

    # Check output that reports an empty string for heating
    room_temperature_controller._refresh_state_from_datapoint(
        datapoint={"pairingID": 48, "value": ""}
    )
    assert room_temperature_controller.heating == 0

    # Check output that affects the heating
    room_temperature_controller._refresh_state_from_datapoint(
        datapoint={"pairingID": 48, "value": "57"}
    )
    assert room_temperature_controller.heating == 57

    # Check output that affects the heating with a float value
    room_temperature_controller._refresh_state_from_datapoint(
        datapoint={"pairingID": 48, "value": "5.7"}
    )
    assert room_temperature_controller.heating == 5

    # Check output that reports an empty string for cooling
    room_temperature_controller._refresh_state_from_datapoint(
        datapoint={"pairingID": 50, "value": ""}
    )
    assert room_temperature_controller.cooling == 0

    # Check output that affects the cooling
    room_temperature_controller._refresh_state_from_datapoint(
        datapoint={"pairingID": 50, "value": "57"}
    )
    assert room_temperature_controller.cooling == 57

    # Check output that affects the cooling with a float value
    room_temperature_controller._refresh_state_from_datapoint(
        datapoint={"pairingID": 50, "value": "5.7"}
    )
    assert room_temperature_controller.cooling == 5

    # Check output that does NOT affects the RTC
    room_temperature_controller._refresh_state_from_datapoint(
        datapoint={"pairingID": 0, "value": "1"},
    )
    assert room_temperature_controller.state is False
    assert room_temperature_controller.target_temperature == 25
    assert room_temperature_controller.eco_mode is True
    assert room_temperature_controller.state_indication == 68
    assert room_temperature_controller.current_temperature == 22.56
    assert room_temperature_controller.heating == 5
    assert room_temperature_controller.cooling == 5


def test_update_device(room_temperature_controller):
    """Test updating the device state."""

    def test_callback():
        pass

    # Ensure callback is registered to test callback code
    room_temperature_controller.register_callback(
        callback_attribute="state", callback=test_callback
    )

    room_temperature_controller.update_device("AL_CONTROLLER_ON_OFF/odp0008", "0")
    assert room_temperature_controller.state is False

    room_temperature_controller.update_device("AL_CONTROLLER_ON_OFF/odp0008", "1")
    assert room_temperature_controller.state is True
