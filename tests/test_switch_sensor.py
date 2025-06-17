"""Test class to test the SwitchSensor device."""

from unittest.mock import AsyncMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.devices.switch_sensor import (
    DimmingSensor,
    DimmingSensorState,
    SwitchSensor,
    SwitchSensorState,
)


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def switch_sensor_with_led(mock_api):
    """Set up the switch-sensor instance for testing the SwitchSensor device."""
    inputs = {
        "idp0000": {"pairingID": 256, "value": "0"},
    }
    outputs = {
        "odp0000": {"pairingID": 1, "value": "0"},
        "odp0001": {"pairingID": 16, "value": ""},
        "odp0006": {"pairingID": 4, "value": ""},
    }
    parameters = {
        "par0007": "2",
    }

    return SwitchSensor(
        device_id="ABB700D9C0A4",
        device_name="Device Name",
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.fixture
def switch_sensor_without_led(mock_api):
    """Set up the switch-sensor instance for testing the SwitchSensor device."""
    inputs = {
        "idp0000": {"pairingID": 256, "value": "0"},
    }
    outputs = {
        "odp0000": {"pairingID": 1, "value": "0"},
        "odp0001": {"pairingID": 16, "value": ""},
        "odp0006": {"pairingID": 4, "value": ""},
    }
    parameters = {
        "par0007": "1",
    }

    return SwitchSensor(
        device_id="ABB700D9C0A4",
        device_name="Device Name",
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.fixture
def dimming_sensor(mock_api):
    """Set up the dimming-sensor instance for testing the DimmingSensor device."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 1, "value": "0"},
        "odp0001": {"pairingID": 16, "value": ""},
        "odp0006": {"pairingID": 4, "value": ""},
    }
    parameters = {}

    return DimmingSensor(
        device_id="ABB700D9C0A4",
        device_name="Device Name",
        channel_id="ch0000",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        api=mock_api,
    )


@pytest.mark.asyncio
async def test_initial_state(switch_sensor_with_led):
    """Test the intial state of the switch-sensor."""
    assert switch_sensor_with_led.state == SwitchSensorState.off.name


@pytest.mark.asyncio
async def test_turn_on_led(switch_sensor_with_led):
    """Test to turning on the led of the sensor."""
    await switch_sensor_with_led.turn_on_led()
    assert switch_sensor_with_led.led is True
    switch_sensor_with_led._api.set_datapoint.assert_called_with(
        device_id="ABB700D9C0A4",
        channel_id="ch0000",
        datapoint="idp0000",
        value="1",
    )


@pytest.mark.asyncio
async def test_turn_off_led(switch_sensor_with_led):
    """Test to turning on the led of the sensor."""
    await switch_sensor_with_led.turn_off_led()
    assert switch_sensor_with_led.led is False
    switch_sensor_with_led._api.set_datapoint.assert_called_with(
        device_id="ABB700D9C0A4",
        channel_id="ch0000",
        datapoint="idp0000",
        value="0",
    )


@pytest.mark.asyncio
async def test_refresh_state_with_led(switch_sensor_with_led):
    """Test refreshing the state of the switch-sensor."""
    switch_sensor_with_led._api.get_datapoint.return_value = ["1"]
    await switch_sensor_with_led.refresh_state()
    assert switch_sensor_with_led.led is True
    switch_sensor_with_led._api.get_datapoint.assert_called_with(
        device_id="ABB700D9C0A4",
        channel_id="ch0000",
        datapoint="idp0000",
    )


@pytest.mark.asyncio
async def test_refresh_state_without_led(switch_sensor_without_led):
    """Test refreshing the state of the switch-sensor."""
    switch_sensor_without_led._api.get_datapoint.return_value = ["1"]
    await switch_sensor_without_led.refresh_state()
    assert switch_sensor_without_led.led is None
    switch_sensor_without_led._api.get_datapoint.assert_called_with(
        device_id="ABB700D9C0A4",
        channel_id="ch0000",
        datapoint="idp0000",
    )


def test_refresh_state_from_datapoint_switch(switch_sensor_with_led):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the state.
    switch_sensor_with_led._refresh_state_from_datapoint(
        datapoint={"pairingID": 1, "value": "1"},
    )
    assert switch_sensor_with_led.state == SwitchSensorState.on.name

    switch_sensor_with_led._refresh_state_from_datapoint(
        datapoint={"pairingID": 1, "value": "INVALID"},
    )
    assert switch_sensor_with_led.state == SwitchSensorState.unknown.name


def test_refresh_state_from_datapoint_dimming(dimming_sensor):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the state.
    dimming_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1, "value": "1"},
    )
    assert dimming_sensor.state == SwitchSensorState.on.name
    assert dimming_sensor.switching_state == SwitchSensorState.on.name

    dimming_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1, "value": "0"},
    )
    assert dimming_sensor.state == SwitchSensorState.off.name
    assert dimming_sensor.switching_state == SwitchSensorState.off.name

    dimming_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 16, "value": "1"},
    )
    assert dimming_sensor.state == DimmingSensorState.longpress_down.name
    assert dimming_sensor.dimming_state == DimmingSensorState.longpress_down.name

    dimming_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 16, "value": "0"},
    )

    assert dimming_sensor.state == DimmingSensorState.longpress_down_release.name
    assert (
        dimming_sensor.dimming_state == DimmingSensorState.longpress_down_release.name
    )

    dimming_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 16, "value": "9"},
    )
    assert dimming_sensor.state == DimmingSensorState.longpress_up.name
    assert dimming_sensor.dimming_state == DimmingSensorState.longpress_up.name

    dimming_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 16, "value": "8"},
    )
    assert dimming_sensor.state == DimmingSensorState.longpress_up_release.name
    assert dimming_sensor.dimming_state == DimmingSensorState.longpress_up_release.name


def test_update_device_with_led(switch_sensor_with_led):
    """Test updating the device state."""

    def test_callback():
        pass

    switch_sensor_with_led.register_callback(
        callback_attribute="led", callback=test_callback
    )

    switch_sensor_with_led.update_device("AL_INFO_ON_OFF/idp0000", "1")
    assert switch_sensor_with_led.led is True

    switch_sensor_with_led.update_device("AL_INFO_ON_OFF/idp0000", "0")
    assert switch_sensor_with_led.led is False


def test_update_device_without_led(switch_sensor_without_led):
    """Test updating the device state."""

    def test_callback():
        pass

    switch_sensor_without_led.register_callback(
        callback_attribute="led", callback=test_callback
    )

    switch_sensor_without_led.update_device("AL_INFO_ON_OFF/idp0000", "1")
    assert switch_sensor_without_led.led is None

    switch_sensor_without_led.update_device("AL_INFO_ON_OFF/idp0000", "0")
    assert switch_sensor_without_led.led is None
