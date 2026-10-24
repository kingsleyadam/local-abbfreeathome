"""Test class to test the RoomTemperatureController channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.function import Function
from src.abbfreeathome.channels.room_temperature_controller import (
    RadiatorActuator,
    RoomTemperatureController,
)
from src.abbfreeathome.const import FUNCTION_CHANNEL_MAPPING
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
def room_temperature_controller(mock_api, mock_device):
    """Set up the RTC instance for testing the RTC channel."""
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

    mock_device.device_serial = "ABB700D72CC9"

    mock_device.api = mock_api
    return RoomTemperatureController(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
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
    room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="ABB700D72CC9",
        channel_id="ch0000",
        datapoint="idp0012",
        value="1",
    )


@pytest.mark.asyncio
async def test_turn_off(room_temperature_controller):
    """Test to turning off the RTC."""
    await room_temperature_controller.turn_off()
    assert room_temperature_controller.state is False
    room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="ABB700D72CC9",
        channel_id="ch0000",
        datapoint="idp0012",
        value="0",
    )


@pytest.mark.asyncio
async def test_eco_on(room_temperature_controller):
    """Test to turning on the eco-mode."""
    await room_temperature_controller.eco_on()
    assert room_temperature_controller.eco_mode is True
    room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="ABB700D72CC9",
        channel_id="ch0000",
        datapoint="idp0011",
        value="1",
    )


@pytest.mark.asyncio
async def test_eco_off(room_temperature_controller):
    """Test to turning off the eco-mode."""
    await room_temperature_controller.eco_off()
    assert room_temperature_controller.eco_mode is False
    room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="ABB700D72CC9",
        channel_id="ch0000",
        datapoint="idp0011",
        value="0",
    )


@pytest.mark.asyncio
async def test_set_temperature(room_temperature_controller):
    """Test to set the target temperatuer of the RTC."""
    await room_temperature_controller.set_temperature(30)
    assert room_temperature_controller.target_temperature == 30
    room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="ABB700D72CC9",
        channel_id="ch0000",
        datapoint="idp0016",
        value="30",
    )
    # Also checking lower and upper boundaries
    await room_temperature_controller.set_temperature(0)
    assert room_temperature_controller.target_temperature == 7
    room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="ABB700D72CC9",
        channel_id="ch0000",
        datapoint="idp0016",
        value="7",
    )
    await room_temperature_controller.set_temperature(50)
    assert room_temperature_controller.target_temperature == 35
    room_temperature_controller.device.api.set_datapoint.assert_called_with(
        device_serial="ABB700D72CC9",
        channel_id="ch0000",
        datapoint="idp0016",
        value="35",
    )


@pytest.mark.asyncio
async def test_refresh_state(room_temperature_controller):
    """Test refreshing state of the RTC."""
    room_temperature_controller.device.api.get_datapoint.return_value = ["1"]
    await room_temperature_controller.refresh_state()
    assert room_temperature_controller.state is True
    room_temperature_controller.device.api.get_datapoint.assert_called_with(
        device_serial="ABB700D72CC9",
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


def test_update_channel(room_temperature_controller):
    """Test updating the channel state."""

    def test_callback():
        pass

    # Ensure callback is registered to test callback code
    room_temperature_controller.register_callback(
        callback_attribute="state", callback=test_callback
    )

    room_temperature_controller.update_channel("AL_CONTROLLER_ON_OFF/odp0008", "0")
    assert room_temperature_controller.state is False

    room_temperature_controller.update_channel("AL_CONTROLLER_ON_OFF/odp0008", "1")
    assert room_temperature_controller.state is True


@pytest.fixture
def radiator_actuator(mock_api, mock_device):
    """Set up a RadiatorActuator instance, a FID_RADIATOR_ACTUATOR_MASTER."""
    inputs = {
        "idp0003": {"pairingID": 57, "value": "0.5"},
        "idp0004": {"pairingID": 58, "value": "0"},
        "idp0005": {"pairingID": 66, "value": "0"},
        "idp0009": {"pairingID": 320, "value": "22"},
    }
    outputs = {
        "odp0000": {"pairingID": 51, "value": "21.5"},
        "odp0002": {"pairingID": 56, "value": "1"},
        "odp0003": {"pairingID": 54, "value": "68"},
        "odp0007": {"pairingID": 304, "value": "20.42"},
        "odp0008": {"pairingID": 331, "value": "0"},
        "odp0009": {"pairingID": 333, "value": "0"},
    }
    parameters = {}

    mock_device.device_serial = "ABB700CF0EFC"
    mock_device.api = mock_api

    return RadiatorActuator(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.mark.asyncio
async def test_radiator_initial_state(radiator_actuator):
    """Test the initial state of the radiator thermostat."""
    assert radiator_actuator.state is True
    assert radiator_actuator.current_temperature == 20.42
    assert radiator_actuator.target_temperature == 21.5
    assert radiator_actuator.eco_mode is True
    assert radiator_actuator.heating_active is False


@pytest.mark.asyncio
async def test_radiator_heating_active(radiator_actuator):
    """Test the heating state comes from AL_HEATING_ACTIVE."""
    assert (
        radiator_actuator._refresh_state_from_datapoint(
            {"pairingID": 331, "value": "1"}
        )
        == "heating_active"
    )
    assert radiator_actuator.heating_active is True


@pytest.mark.asyncio
async def test_radiator_heating_demand(radiator_actuator):
    """Test the heating value comes from AL_HEATING_DEMAND."""
    assert (
        radiator_actuator._refresh_state_from_datapoint(
            {"pairingID": 333, "value": "55"}
        )
        == "heating"
    )
    assert radiator_actuator.heating == 55
    assert radiator_actuator.heating_active is True


@pytest.mark.asyncio
async def test_radiator_unparsable_heating_demand(radiator_actuator):
    """Test an empty heating demand does not raise."""
    radiator_actuator._refresh_state_from_datapoint({"pairingID": 333, "value": ""})
    assert radiator_actuator.heating == 0


@pytest.mark.asyncio
async def test_radiator_inherits_room_temperature_controller(radiator_actuator):
    """Test the inherited datapoints are still handled."""
    assert (
        radiator_actuator._refresh_state_from_datapoint(
            {"pairingID": 304, "value": "19.5"}
        )
        == "current_temperature"
    )
    assert radiator_actuator.current_temperature == 19.5


@pytest.mark.asyncio
async def test_radiator_set_temperature(radiator_actuator):
    """Test setting the target temperature of the radiator thermostat."""
    await radiator_actuator.set_temperature(21.5)
    assert radiator_actuator.target_temperature == 21.5
    radiator_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB700CF0EFC",
        channel_id="ch0000",
        datapoint="idp0009",
        value="21.5",
    )


@pytest.mark.asyncio
async def test_radiator_turn_off(radiator_actuator):
    """Test turning off the radiator thermostat."""
    await radiator_actuator.turn_off()
    assert radiator_actuator.state is False
    radiator_actuator.device.api.set_datapoint.assert_called_with(
        device_serial="ABB700CF0EFC",
        channel_id="ch0000",
        datapoint="idp0005",
        value="0",
    )


def test_radiator_is_mapped_to_its_function():
    """Test the function id reaches the channel mapping."""
    assert (
        FUNCTION_CHANNEL_MAPPING[Function.FID_RADIATOR_ACTUATOR_MASTER]
        is RadiatorActuator
    )
