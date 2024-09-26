"""Test functions in bin."""

from unittest.mock import mock_open, patch

# Assuming the function is in a module named 'module_name'
from abbfreeathome.bin.function_id import load_functions_from_json_file
from abbfreeathome.bin.pairing_id import load_pairings_from_json_file


def test_load_functions_from_json_file(capsys):
    """Test the load_functions_from_json_file function."""
    # Mock JSON data
    mock_json_data = """
    [
        {"Function ID (hex)": "0x0000", "Name": "FID_SWITCH_SENSOR"},
        {"Function ID (hex)": "0x0007", "Name": "FID_SWITCH_ACTUATOR"},
        {"Function ID (hex)": "0x000E", "Name": "FID_RAIN_ALARM_SENSOR"}
    ]
    """

    # Use mock_open to simulate file opening and reading
    mock_open_file = mock_open(read_data=mock_json_data)

    with (
        patch("builtins.open", mock_open_file),
        patch(
            "json.load",
            return_value=[
                {"Function ID (hex)": "0x0000", "Name": "FID_SWITCH_SENSOR"},
                {"Function ID (hex)": "0x0007", "Name": "FID_SWITCH_ACTUATOR"},
                {"Function ID (hex)": "0x000E", "Name": "FID_RAIN_ALARM_SENSOR"},
            ],
        ),
    ):
        load_functions_from_json_file("dummy_path")

    # Capture the output
    captured = capsys.readouterr()

    # Check the output
    assert "FID_SWITCH_SENSOR = '0'" in captured.out
    assert "FID_SWITCH_ACTUATOR = '7'" in captured.out
    assert "FID_RAIN_ALARM_SENSOR = 'e'" in captured.out


def test_load_pairings_from_json_file(capsys):
    """Test the load_pairings_from_json_file function."""
    # Mock JSON data
    mock_json_data = """
    [
        {"Pairing ID (dec)": "0", "Name": "AL_INVALID"},
        {"Pairing ID (dec)": "1", "Name": "AL_SWITCH_ON_OFF"},
        {"Pairing ID (dec)": "2", "Name": "AL_TIMED_START_STOP"}
    ]
    """

    # Use mock_open to simulate file opening and reading
    mock_open_file = mock_open(read_data=mock_json_data)

    with (
        patch("builtins.open", mock_open_file),
        patch(
            "json.load",
            return_value=[
                {"Pairing ID (dec)": "0", "Name": "AL_INVALID"},
                {"Pairing ID (dec)": "1", "Name": "AL_SWITCH_ON_OFF"},
                {"Pairing ID (dec)": "2", "Name": "AL_TIMED_START_STOP"},
            ],
        ),
    ):
        load_pairings_from_json_file("dummy_path")

    # Capture the output
    captured = capsys.readouterr()

    # Check the output
    assert "AL_INVALID = 0" in captured.out
    assert "AL_SWITCH_ON_OFF = 1" in captured.out
    assert "AL_TIMED_START_STOP = 2" in captured.out
