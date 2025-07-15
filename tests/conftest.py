"""Shared test fixtures for the ABB-Free@Home test suite."""

import pytest

from src.abbfreeathome.floorplan import Floorplan


@pytest.fixture
def mock_floorplan():
    """Create a mock floorplan for testing with realistic data."""
    # Based on the real API dump structure
    floorplan_data = {
        "01": {
            "name": "Ground Floor",
            "rooms": {
                "04": {"name": "Toilet"},
                "18": {"name": "Living Room"},
                "0C": {"name": "Kitchen"},
                "13": {"name": "Entry"},
            },
        },
        "02": {
            "name": "1st Floor",
            "rooms": {
                "06": {"name": "Living Room"},
            },
        },
        "03": {
            "name": "2nd Floor",
            "rooms": {
                "07": {"name": "Landing"},
                "08": {"name": "Large Bedroom"},
                "09": {"name": "Bathroom"},
                "0A": {"name": "Small Bedroom"},
                "0D": {"name": "Primary Bedroom"},
                "15": {"name": "Closet"},
            },
        },
        "04": {
            "name": "3rd Floor",
            "rooms": {
                "0B": {"name": "Spare Bedroom"},
                "0F": {"name": "Office"},
                "10": {"name": "Guest Bathroom"},
                "12": {"name": "Landing"},
                "19": {"name": "Closet"},
                "1A": {"name": "Guest Bedroom"},
                "1B": {"name": "Laundry Room"},
            },
        },
    }

    return Floorplan(floorplan_data)
