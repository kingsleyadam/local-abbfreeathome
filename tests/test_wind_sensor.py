"""Test class to test the WindSensor channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.wind_sensor import WindSensor
from src.abbfreeathome.device import Device


def get_wind_sensor(mock_api, mock_device):
    """Get the WindSensor class to be tested against."""
    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 37, "value": "0"},
        "odp0001": {"pairingID": 1025, "value": "3"},
        "odp0002": {"pairingID": 4, "value": "0"},
        "odp0003": {"pairingID": 1028, "value": "10.3"},
    }
    parameters = {"par002e": "5", "par0047": "2", "par0048": "7"}

    return WindSensor(
        device=mock_device,
        channel_id="ch0003",
        channel_name="Channel Name",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def wind_sensor(mock_api, mock_device):
    """Set up the instance for testing the WindSensor channel."""
    mock_device.device_serial = "7EB1000021C5"

    mock_device.api = mock_api
    return get_wind_sensor(mock_api, mock_device)


@pytest.fixture
def mock_device():
    """Create a mock device function."""
    return MagicMock(spec=Device)


@pytest.mark.asyncio
async def test_initial_state(wind_sensor):
    """Test the intial state of the sensor."""
    assert wind_sensor.state == 10.3
    assert wind_sensor.alarm is False
    assert wind_sensor.force == 3


@pytest.mark.asyncio
async def test_refresh_state(wind_sensor):
    """Test refreshing the state of the sensor."""
    wind_sensor.device.api.get_datapoint.return_value = ["1"]
    await wind_sensor.refresh_state()
    assert wind_sensor.state == 1.0
    assert wind_sensor.alarm is True
    assert wind_sensor.force == 1
    wind_sensor.device.api.get_datapoint.assert_called_with(
        device_serial="7EB1000021C5",
        channel_id="ch0003",
        datapoint="odp0001",
    )


@pytest.mark.asyncio
async def test_refresh_state_notifies_callbacks(wind_sensor):
    """Cache the values read and notify the callbacks of every attribute."""
    callbacks = {attribute: MagicMock() for attribute in ("state", "alarm", "force")}
    for attribute, callback in callbacks.items():
        wind_sensor.register_callback(callback_attribute=attribute, callback=callback)
    wind_sensor.device.api.get_datapoint.side_effect = [["12.5"], ["1"], ["6"]]

    await wind_sensor.refresh_state()

    assert wind_sensor.state == 12.5
    assert wind_sensor.alarm is True
    assert wind_sensor.force == 6
    assert wind_sensor._outputs["odp0003"]["value"] == "12.5"
    assert wind_sensor._outputs["odp0000"]["value"] == "1"
    assert wind_sensor._outputs["odp0001"]["value"] == "6"
    for callback in callbacks.values():
        callback.assert_called_once_with()


@pytest.mark.asyncio
async def test_priming_after_refresh_state(wind_sensor):
    """Compare a reconnect snapshot against the refreshed value, not the old one."""
    callback = MagicMock()
    wind_sensor.register_callback(callback_attribute="force", callback=callback)
    wind_sensor.device.api.get_datapoint.return_value = ["6"]
    await wind_sensor.refresh_state()
    callback.reset_mock()

    wind_sensor.update_channel("7EB1000021C5/ch0003/odp0001", "3", is_priming=True)

    assert wind_sensor.force == 3
    callback.assert_called_once_with()


def test_refresh_state_from_datapoint(wind_sensor):
    """Test the _refresh_state_from_datapoint function."""
    # Check output that affects the state.
    wind_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1028, "value": "20.1"},
    )
    assert wind_sensor.state == 20.1

    # Check output that affects the state.
    wind_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 37, "value": "1"},
    )
    assert wind_sensor.alarm is True

    # Check output that affects the state.
    wind_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1025, "value": "2"},
    )
    assert wind_sensor.force == 2

    # Check output that does NOT affect the state.
    wind_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 4, "value": "1"},
    )
    assert wind_sensor.state == 20.1


@pytest.mark.parametrize("value", ["invalid", "", None])
def test_refresh_state_from_datapoint_non_numeric(wind_sensor, value):
    """Test that non-numeric speed and force values are unknown."""
    wind_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1028, "value": value},
    )
    assert wind_sensor.state is None

    wind_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1025, "value": value},
    )
    assert wind_sensor.force is None
