"""Shared test fixtures for the ABB-Free@Home test suite."""

from inspect import signature
from unittest.mock import Mock

import aiohttp.client_reqrep
import pytest

from src.abbfreeathome.floorplan import Floorplan


@pytest.fixture(scope="session", autouse=True)
def _patch_aiohttp_clientresponse_stream_writer():
    """Work around aioresponses not passing aiohttp's required stream_writer kwarg."""
    original_init = aiohttp.client_reqrep.ClientResponse.__init__

    # See: https://github.com/pnuckowski/aioresponses/issues/289
    if "stream_writer" not in signature(original_init).parameters:
        yield
        return

    def patched_init(self, method, url, *args, **kwargs):
        kwargs.setdefault("stream_writer", Mock())
        return original_init(self, method, url, *args, **kwargs)

    aiohttp.client_reqrep.ClientResponse.__init__ = patched_init
    yield
    aiohttp.client_reqrep.ClientResponse.__init__ = original_init


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
