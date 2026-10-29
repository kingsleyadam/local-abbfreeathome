"""Tests for the heating/cooling changeover sensor."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.pairing import Pairing
from src.abbfreeathome.channels.heating_cooling_sensor import (
    HeatingCoolingSensor,
    HeatingCoolingSensorState,
)
from src.abbfreeathome.device import Device


@pytest.fixture
def heating_cooling_sensor(mock_floorplan):
    """Load the sensor through device discovery using the reported channel."""
    device = Device(
        device_serial="ABB204E73951",
        device_id="TEST",
        display_name="Test Device",
        api=AsyncMock(spec=FreeAtHomeApi),
        channels_data={
            "ch0000": {
                "functionID": "002A",
                "displayName": "Heating / Cooling Changeover",
                "outputs": {
                    "odp0007": {
                        "pairingID": 309,
                        "value": "1",
                    },
                    "odp0008": {
                        "pairingID": Pairing.AL_INFO_ON_OFF.value,
                        "value": "0",
                    },
                },
                "parameters": {"par0010": "1"},
            },
        },
    )
    return device.load_channels(mock_floorplan)["ch0000"]


def test_discovery_and_initial_state(heating_cooling_sensor):
    """Discover FID 0x2A and initialize state from AL_HEATING_COOLING."""
    assert isinstance(heating_cooling_sensor, HeatingCoolingSensor)
    assert heating_cooling_sensor.state == HeatingCoolingSensorState.cooling.name


@pytest.mark.parametrize(("value", "expected"), [("0", "heating"), ("1", "cooling")])
def test_initial_state(value, expected):
    """Decode ABB's mode values without reinterpreting the contact type."""
    sensor = HeatingCoolingSensor(
        device=MagicMock(spec=Device),
        channel_id="ch0000",
        channel_name="Changeover",
        inputs={},
        outputs={"odp0007": {"pairingID": 309, "value": value}},
        parameters={"par0010": "1"},
    )
    assert sensor.state == expected


def test_missing_changeover_output():
    """Leave state unknown when the changeover output is absent."""
    sensor = HeatingCoolingSensor(
        device=MagicMock(spec=Device),
        channel_id="ch0000",
        channel_name="Changeover",
        inputs={},
        outputs={"odp0000": {"pairingID": 256, "value": "1"}},
        parameters={},
    )
    assert sensor.state == HeatingCoolingSensorState.unknown.name


@pytest.mark.asyncio
async def test_refresh_state(heating_cooling_sensor):
    """Refresh the changeover output from the API."""
    heating_cooling_sensor.device.api.get_datapoint.return_value = ["0"]

    await heating_cooling_sensor.refresh_state()

    assert heating_cooling_sensor.state == HeatingCoolingSensorState.heating.name
    heating_cooling_sensor.device.api.get_datapoint.assert_awaited_once_with(
        device_serial="ABB204E73951",
        channel_id="ch0000",
        datapoint="odp0007",
    )


def test_updates_notify_state_subscribers(heating_cooling_sensor):
    """Apply changeover updates and notify state subscribers in both directions."""
    callback = MagicMock()
    heating_cooling_sensor.register_callback("state", callback)

    for value, expected in [("0", "heating"), ("1", "cooling")]:
        callback.reset_mock()
        heating_cooling_sensor.update_channel("ABB204E73951/ch0000/odp0007", value)
        assert heating_cooling_sensor.state == expected
        callback.assert_called_once_with()


def test_unrelated_update_ignored(heating_cooling_sensor):
    """Ignore other output pairings without notifying state subscribers."""
    callback = MagicMock()
    heating_cooling_sensor.register_callback("state", callback)

    heating_cooling_sensor.update_channel("ABB204E73951/ch0000/odp0008", "1")

    assert heating_cooling_sensor.state == HeatingCoolingSensorState.cooling.name
    callback.assert_not_called()


@pytest.mark.parametrize("value", ["", "2", "invalid", None, 0, 1, False, [], {}])
def test_invalid_value_sets_unknown(heating_cooling_sensor, caplog, value):
    """Report malformed values as unknown, warn, and recover on valid data."""
    callback = MagicMock()
    heating_cooling_sensor.register_callback("state", callback)
    datapoint = {"pairingID": 309, "value": value}

    attributes = heating_cooling_sensor._refresh_state_from_datapoint(datapoint)

    assert heating_cooling_sensor.state == HeatingCoolingSensorState.unknown.name
    assert attributes == ["state"]
    assert "Invalid heating/cooling value" in caplog.text
    assert heating_cooling_sensor.channel_name in caplog.text

    heating_cooling_sensor.update_channel("ABB204E73951/ch0000/odp0007", "0")

    assert heating_cooling_sensor.state == HeatingCoolingSensorState.heating.name
    callback.assert_called_once_with()


def test_missing_value_sets_unknown(heating_cooling_sensor, caplog):
    """Treat a missing value as unknown rather than off."""
    attributes = heating_cooling_sensor._refresh_state_from_datapoint(
        {"pairingID": 309}
    )

    assert heating_cooling_sensor.state == HeatingCoolingSensorState.unknown.name
    assert attributes == ["state"]
    assert "Invalid heating/cooling value None" in caplog.text


def test_invalid_update_notifies_subscribers(heating_cooling_sensor):
    """Notify subscribers when an update changes the state to unknown."""
    callback = MagicMock()
    heating_cooling_sensor.register_callback("state", callback)

    heating_cooling_sensor.update_channel("ABB204E73951/ch0000/odp0007", "invalid")

    assert heating_cooling_sensor.state == HeatingCoolingSensorState.unknown.name
    callback.assert_called_once_with()
