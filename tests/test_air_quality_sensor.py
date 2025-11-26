"""Test class to test the AirQualitySensor channel."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.pairing import Pairing
from src.abbfreeathome.channels.air_quality_sensor import AirQualitySensor
from src.abbfreeathome.device import Device


def get_air_quality_sensor(mock_api, mock_device):
    """Get the AirQualitySensor class to be tested against."""
    # Set the api on the mock device so channels can access it
    mock_device.api = mock_api

    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 1563, "value": "1669.12"},  # AL_INFO_CO_2
        "odp0001": {"pairingID": 1576, "value": "1"},  # AL_CO2_ALERT
        "odp0002": {"pairingID": 1570, "value": "193"},  # AL_INFO_VOC_INDEX
        "odp0003": {"pairingID": 1577, "value": "1"},  # AL_VOC_ALERT
        "odp0004": {"pairingID": 337, "value": "52"},  # AL_HUMIDITY
    }
    parameters = {
        "par0176": "2",  # PID_ENABLE_CO2_ALERT
        "par0170": "1000",  # PID_CO2_ALERT_ACTIVATION_LEVEL
        "par0177": "2",  # PID_ENABLE_VOC_ALERT
        "par0171": "150",  # PID_VOC_ALERT_ACTIVATION_LEVEL
        "par0178": "2",  # PID_ENABLE_HUMIDITY_ALERT
        "par0174": "30",  # PID_HUMIDITY_ALERT_LOWER_LIMIT
        "par0175": "70",  # PID_HUMIDITY_ALERT_UPPER_LIMIT
    }

    return AirQualitySensor(
        device=mock_device,
        channel_id="ch0016",
        channel_name="Tenton IAQ",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )


@pytest.fixture
def mock_api():
    """Create a mock api function."""
    return AsyncMock(spec=FreeAtHomeApi)


@pytest.fixture
def air_quality_sensor(mock_api, mock_device):
    """Set up the instance for testing the AirQualitySensor channel."""
    mock_device.device_serial = "ABB7F631EXXX"
    return get_air_quality_sensor(mock_api, mock_device)


@pytest.fixture
def mock_device():
    """Create a mock device function."""
    return MagicMock(spec=Device)


@pytest.mark.asyncio
async def test_initial_state(air_quality_sensor):
    """Test the initial state of the sensor."""
    assert air_quality_sensor.co2 == 1669.12
    assert air_quality_sensor.co2_alert is True
    assert air_quality_sensor.voc_index == 193
    assert air_quality_sensor.voc_alert is True
    assert air_quality_sensor.humidity == 52


@pytest.mark.asyncio
async def test_initial_state_no_alerts(mock_api, mock_device):
    """Test the initial state of the sensor with no alerts."""
    mock_device.device_serial = "ABB7F631EXXX"
    mock_device.api = mock_api

    inputs = {}
    outputs = {
        "odp0000": {"pairingID": 1563, "value": "500.0"},  # AL_INFO_CO_2
        "odp0001": {"pairingID": 1576, "value": "0"},  # AL_CO2_ALERT
        "odp0002": {"pairingID": 1570, "value": "100"},  # AL_INFO_VOC_INDEX
        "odp0003": {"pairingID": 1577, "value": "0"},  # AL_VOC_ALERT
        "odp0004": {"pairingID": 337, "value": "45"},  # AL_HUMIDITY
    }
    parameters = {}

    sensor = AirQualitySensor(
        device=mock_device,
        channel_id="ch0016",
        channel_name="Tenton IAQ",
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
    )

    assert sensor.co2 == 500.0
    assert sensor.co2_alert is False
    assert sensor.voc_index == 100
    assert sensor.voc_alert is False
    assert sensor.humidity == 45


@pytest.mark.asyncio
async def test_refresh_state(air_quality_sensor):
    """Test refreshing the state of the sensor."""
    # Mock the API to return different values for each pairing
    air_quality_sensor.device.api.get_datapoint.side_effect = [
        ["850.5"],  # CO2
        ["0"],  # CO2 Alert
        ["120"],  # VOC Index
        ["0"],  # VOC Alert
        ["65"],  # Humidity
    ]

    await air_quality_sensor.refresh_state()

    assert air_quality_sensor.co2 == 850.5
    assert air_quality_sensor.co2_alert is False
    assert air_quality_sensor.voc_index == 120
    assert air_quality_sensor.voc_alert is False
    assert air_quality_sensor.humidity == 65


def test_refresh_state_from_datapoint_co2(air_quality_sensor):
    """Test the _refresh_state_from_datapoint function for CO2."""
    # Test CO2 concentration
    result = air_quality_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1563, "value": "850.5"},
    )
    assert result == "co2"
    assert air_quality_sensor.co2 == 850.5

    # Test CO2 alert
    result = air_quality_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1576, "value": "0"},
    )
    assert result == "co2_alert"
    assert air_quality_sensor.co2_alert is False


def test_refresh_state_from_datapoint_voc(air_quality_sensor):
    """Test the _refresh_state_from_datapoint function for VOC."""
    # Test VOC index
    result = air_quality_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1570, "value": "120"},
    )
    assert result == "voc_index"
    assert air_quality_sensor.voc_index == 120

    # Test VOC alert
    result = air_quality_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 1577, "value": "0"},
    )
    assert result == "voc_alert"
    assert air_quality_sensor.voc_alert is False


def test_refresh_state_from_datapoint_humidity(air_quality_sensor):
    """Test the _refresh_state_from_datapoint function for humidity."""
    result = air_quality_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 337, "value": "65"},
    )
    assert result == "humidity"
    assert air_quality_sensor.humidity == 65


def test_refresh_state_from_datapoint_invalid(air_quality_sensor):
    """Test the _refresh_state_from_datapoint function with invalid pairing."""
    # Check output that does NOT affect the state
    result = air_quality_sensor._refresh_state_from_datapoint(
        datapoint={"pairingID": 9999, "value": "1"},
    )
    assert result is None
    # Ensure no state changed
    assert air_quality_sensor.co2 == 1669.12
    assert air_quality_sensor.voc_index == 193
    assert air_quality_sensor.humidity == 52


def test_all_properties(air_quality_sensor):
    """Test all properties return expected values."""
    assert air_quality_sensor.co2 == 1669.12
    assert air_quality_sensor.co2_alert is True
    assert air_quality_sensor.voc_index == 193
    assert air_quality_sensor.voc_alert is True
    assert air_quality_sensor.humidity == 52


def test_callback_attributes(air_quality_sensor):
    """Test that callback attributes are properly defined."""
    assert "co2" in air_quality_sensor._callback_attributes
    assert "co2_alert" in air_quality_sensor._callback_attributes
    assert "voc_index" in air_quality_sensor._callback_attributes
    assert "voc_alert" in air_quality_sensor._callback_attributes
    assert "humidity" in air_quality_sensor._callback_attributes


def test_state_refresh_pairings(air_quality_sensor):
    """Test that state refresh pairings are properly defined."""
    assert Pairing.AL_INFO_CO_2 in air_quality_sensor._state_refresh_pairings
    assert Pairing.AL_CO2_ALERT in air_quality_sensor._state_refresh_pairings
    assert Pairing.AL_INFO_VOC_INDEX in air_quality_sensor._state_refresh_pairings
    assert Pairing.AL_VOC_ALERT in air_quality_sensor._state_refresh_pairings
    assert Pairing.AL_HUMIDITY in air_quality_sensor._state_refresh_pairings
