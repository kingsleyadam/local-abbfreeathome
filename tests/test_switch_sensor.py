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
def switch_sensor(mock_api):
    """Set up the switch-sensor instance for testing the SwitchSensor device."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 1, "value": "0"},
        "odp0001": {"pairingID": 16, "value": ""},
        "odp0006": {"pairingID": 4, "value": ""},
    }
    parameters = {}

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
async def test_initial_state(switch_sensor):
    """Test the intial state of the switch-sensor."""
    assert switch_sensor.state == SwitchSensorState.off.name


@pytest.mark.asyncio
async def test_refresh_state(switch_sensor):
    """Test refreshing the state of the switch-sensor."""
    switch_sensor._api.get_datapoint.return_value = ["1"]
    await switch_sensor.refresh_state()
    assert switch_sensor.state == SwitchSensorState.on.name
    switch_sensor._api.get_datapoint.assert_called_with(
        device_id="ABB700D9C0A4",
        channel_id="ch0000",
        datapoint="odp0000",
    )


def test_refresh_state_from_output_switch(switch_sensor):
    """Test the _refresh_state_from_output function."""
    # Check output that affects the state.
    switch_sensor._refresh_state_from_output(
        output={"pairingID": 1, "value": "1"},
    )
    assert switch_sensor.state == SwitchSensorState.on.name

    switch_sensor._refresh_state_from_output(
        output={"pairingID": 1, "value": "INVALID"},
    )
    assert switch_sensor.state == SwitchSensorState.unknown.name


def test_refresh_state_from_output_dimming(dimming_sensor):
    """Test the _refresh_state_from_output function."""
    # Check output that affects the state.
    dimming_sensor._refresh_state_from_output(
        output={"pairingID": 1, "value": "1"},
    )
    assert dimming_sensor.state == SwitchSensorState.on.name
    assert dimming_sensor.switching_state == SwitchSensorState.on.name

    dimming_sensor._refresh_state_from_output(
        output={"pairingID": 1, "value": "0"},
    )
    assert dimming_sensor.state == SwitchSensorState.off.name
    assert dimming_sensor.switching_state == SwitchSensorState.off.name

    dimming_sensor._refresh_state_from_output(
        output={"pairingID": 16, "value": "1"},
    )
    assert dimming_sensor.state == DimmingSensorState.longpress_down.name
    assert dimming_sensor.dimming_state == DimmingSensorState.longpress_down.name

    dimming_sensor._refresh_state_from_output(
        output={"pairingID": 16, "value": "0"},
    )

    assert dimming_sensor.state == DimmingSensorState.longpress_down_release.name
    assert (
        dimming_sensor.dimming_state == DimmingSensorState.longpress_down_release.name
    )

    dimming_sensor._refresh_state_from_output(
        output={"pairingID": 16, "value": "9"},
    )
    assert dimming_sensor.state == DimmingSensorState.longpress_up.name
    assert dimming_sensor.dimming_state == DimmingSensorState.longpress_up.name

    dimming_sensor._refresh_state_from_output(
        output={"pairingID": 16, "value": "8"},
    )
    assert dimming_sensor.state == DimmingSensorState.longpress_up_release.name
    assert dimming_sensor.dimming_state == DimmingSensorState.longpress_up_release.name
