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
    assert room_temperature_controller.heating_mode is False
    assert room_temperature_controller.heating_cooling_active is True
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
    assert radiator_actuator._refresh_state_from_datapoint(
        {"pairingID": 331, "value": "1"}
    ) == ["heating_active"]
    assert radiator_actuator.heating_active is True


@pytest.mark.asyncio
async def test_radiator_heating_demand(radiator_actuator):
    """Test the heating value comes from AL_HEATING_DEMAND."""
    assert radiator_actuator._refresh_state_from_datapoint(
        {"pairingID": 333, "value": "55"}
    ) == ["heating", "heating_active"]
    assert radiator_actuator.heating == 55
    assert radiator_actuator.heating_active is True


@pytest.mark.parametrize("is_priming", [False, True])
def test_radiator_demand_notifies_heating_active(radiator_actuator, is_priming):
    """Demand transitions notify both groups, including changed priming updates."""
    active_states = []
    heating_callback = MagicMock()
    active_callback = MagicMock(
        side_effect=lambda: active_states.append(radiator_actuator.heating_active)
    )
    radiator_actuator.register_callback("heating", heating_callback)
    radiator_actuator.register_callback("heating_active", active_callback)

    for demand in ("55", "0"):
        radiator_actuator.update_channel(
            "AL_HEATING_DEMAND/odp0009", demand, is_priming=is_priming
        )
        assert radiator_actuator.heating == int(demand)

    assert radiator_actuator._outputs["odp0008"]["value"] == "0"
    assert active_states == [True, False]
    assert heating_callback.call_count == 2
    assert active_callback.call_count == 2

    radiator_actuator.update_channel("AL_HEATING_DEMAND/odp0009", "0", is_priming=True)
    assert heating_callback.call_count == 2
    assert active_callback.call_count == 2


@pytest.mark.parametrize(
    ("active_flag", "initial_demand", "demand"),
    [("0", "55", "60"), ("1", "0", "55"), ("1", "55", "0")],
)
def test_radiator_demand_preserves_heating_active(
    radiator_actuator, active_flag, initial_demand, demand
):
    """Demand changes that leave the effective boolean unchanged notify heating only."""
    radiator_actuator.update_channel("AL_HEATING_ACTIVE/odp0008", active_flag)
    radiator_actuator.update_channel("AL_HEATING_DEMAND/odp0009", initial_demand)
    heating_callback = MagicMock()
    active_callback = MagicMock()
    radiator_actuator.register_callback("heating", heating_callback)
    radiator_actuator.register_callback("heating_active", active_callback)

    radiator_actuator.update_channel("AL_HEATING_DEMAND/odp0009", demand)

    assert radiator_actuator.heating == int(demand)
    assert radiator_actuator.heating_active is True
    heating_callback.assert_called_once_with()
    active_callback.assert_not_called()


def test_radiator_active_flag_notifies_subscribers(radiator_actuator):
    """Direct flag updates notify active subscribers without heating callbacks."""
    heating_callback = MagicMock()
    active_states = []
    radiator_actuator.register_callback("heating", heating_callback)
    radiator_actuator.register_callback(
        "heating_active",
        lambda: active_states.append(radiator_actuator.heating_active),
    )

    for active_flag in ("1", "0"):
        radiator_actuator.update_channel("AL_HEATING_ACTIVE/odp0008", active_flag)

    assert active_states == [True, False]
    heating_callback.assert_not_called()


@pytest.mark.asyncio
async def test_radiator_unparsable_heating_demand(radiator_actuator):
    """Test an empty heating demand does not raise."""
    radiator_actuator._refresh_state_from_datapoint({"pairingID": 333, "value": ""})
    assert radiator_actuator.heating == 0


@pytest.mark.asyncio
async def test_radiator_inherits_room_temperature_controller(radiator_actuator):
    """Test the inherited datapoints are still handled."""
    assert radiator_actuator._refresh_state_from_datapoint(
        {"pairingID": 304, "value": "19.5"}
    ) == ["current_temperature"]
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


@pytest.mark.parametrize("channel_class", [RoomTemperatureController, RadiatorActuator])
@pytest.mark.parametrize(
    ("indication", "heating_mode", "active", "eco_mode"),
    [
        ("65", False, False, False),
        ("33", True, True, False),
        ("68", False, False, True),
        ("96", True, False, False),
        ("1", False, True, False),
        ("37", True, True, True),
        ("0", False, True, False),
    ],
)
def test_state_indication_bits(
    mock_device, channel_class, indication, heating_mode, active, eco_mode
):
    """Decode reported idle/heating values and active cooling for both channels."""
    channel = channel_class(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Thermostat",
        inputs={},
        outputs={"odp0003": {"pairingID": 54, "value": indication}},
        parameters={},
    )

    assert channel.state_indication == int(indication)
    assert channel.heating_mode is heating_mode
    assert channel.heating_cooling_active is active
    assert channel.eco_mode is eco_mode


@pytest.mark.parametrize("channel_class", [RoomTemperatureController, RadiatorActuator])
def test_missing_state_indication(mock_device, channel_class):
    """Keep mode and activity unknown until a state indication arrives."""
    channel = channel_class(
        device=mock_device,
        channel_id="ch0000",
        channel_name="Thermostat",
        inputs={},
        outputs={},
        parameters={},
    )

    assert channel.state_indication is None
    assert channel.heating_mode is None
    assert channel.heating_cooling_active is None
    assert channel.eco_mode is None

    channel._refresh_state_from_datapoint({"pairingID": 54, "value": "33"})

    assert channel.heating_mode is True
    assert channel.heating_cooling_active is True


@pytest.mark.parametrize(
    ("fixture_name", "datapoint"),
    [
        ("room_temperature_controller", "odp0009"),
        ("radiator_actuator", "odp0003"),
    ],
)
def test_state_indication_callbacks(request, fixture_name, datapoint):
    """Notify subscribers after decoding mode, activity, eco, and raw state."""
    channel = request.getfixturevalue(fixture_name)
    attributes = (
        "state_indication",
        "eco_mode",
        "heating_mode",
        "heating_cooling_active",
    )
    callbacks = {attribute: MagicMock() for attribute in attributes}
    observed_states = []
    for attribute, callback in callbacks.items():
        channel.register_callback(attribute, callback)

    def shared_callback():
        observed_states.append(
            (
                channel.state_indication,
                channel.heating_mode,
                channel.heating_cooling_active,
            )
        )

    for attribute in attributes:
        channel.register_callback(attribute, shared_callback)

    for indication in ("33", "1", "96", "68"):
        channel.update_channel(f"AL_STATE_INDICATION/{datapoint}", indication)

    assert observed_states == [
        (33, True, True),
        (1, False, True),
        (96, True, False),
        (68, False, False),
    ]
    assert channel.eco_mode is True
    for callback in callbacks.values():
        assert callback.call_count == 4


def test_cooling_demand_does_not_override_inactive_indication(
    room_temperature_controller,
):
    """Keep an idle room inactive despite a nonzero cooling demand."""
    room_temperature_controller.update_channel(
        "AL_ACTUATING_VALUE_COOLING/odp0001", "100"
    )

    assert room_temperature_controller.cooling == 100
    assert room_temperature_controller.state_indication == 65
    assert room_temperature_controller.heating_cooling_active is False
