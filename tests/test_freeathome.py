"""Test code to test all FreeAtHome class."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from abbfreeathome.api import FreeAtHomeApi
from abbfreeathome.bin.function_id import FunctionID
from abbfreeathome.bin.interface import Interface
from abbfreeathome.devices.switch_actuator import SwitchActuator
from abbfreeathome.freeathome import FreeAtHome


@pytest.fixture
def api_mock():
    """Mock-up the api class."""
    api = AsyncMock(spec=FreeAtHomeApi)
    api.get_configuration.return_value = {
        "floorplan": {
            "floors": {
                "01": {
                    "name": "Ground Floor",
                    "rooms": {"01": {"name": "Living Room"}},
                },
                "02": {"name": "First Floor", "rooms": {"02": {"name": "Bedroom"}}},
            }
        },
        "devices": {
            "ABB7F500E17A": {
                "deviceReboots": "28",
                "floor": "01",
                "room": "01",
                "interface": "TP",
                "deviceId": "910C",
                "displayName": "Study Area Rocker",
                "unresponsive": False,
                "unresponsiveCounter": 0,
                "defect": False,
                "channels": {
                    "ch0000": {
                        "floor": "01",
                        "room": "01",
                        "displayName": "Study Area Rocker",
                        "functionID": "0",
                        "inputs": {
                            "idp0000": {"pairingID": 256, "value": "0"},
                            "idp0001": {"pairingID": 18, "value": "0"},
                            "idp0002": {"pairingID": 273, "value": "0"},
                            "idp0004": {"pairingID": 261, "value": "0"},
                            "idp0005": {"pairingID": 278, "value": "0"},
                        },
                        "outputs": {
                            "odp0000": {"pairingID": 1, "value": "0"},
                            "odp0006": {"pairingID": 4, "value": "0"},
                        },
                        "parameters": {
                            "par0002": "50",
                            "par0001": "50",
                            "par0007": "1",
                        },
                    },
                    "ch0003": {
                        "floor": "01",
                        "room": "01",
                        "displayName": "Study Area Light",
                        "selectedIcon": "1",
                        "functionID": "7",
                        "inputs": {
                            "idp0000": {"pairingID": 1, "value": "0"},
                            "idp0001": {"pairingID": 2, "value": "0"},
                            "idp0002": {"pairingID": 3, "value": "0"},
                            "idp0003": {"pairingID": 4, "value": "1"},
                            "idp0004": {"pairingID": 6, "value": "0"},
                        },
                        "outputs": {
                            "odp0000": {"pairingID": 256, "value": "0"},
                            "odp0001": {"pairingID": 257, "value": "0"},
                        },
                        "parameters": {"par0015": "360", "par0014": "1"},
                    },
                },
                "parameters": {"par00ed": "1"},
            },
            "ABB7F62F6C0B": {
                "deviceReboots": "23",
                "floor": "02",
                "room": "02",
                "interface": "TP",
                "deviceId": "910C",
                "displayName": "Bedroom Rocker",
                "unresponsive": False,
                "unresponsiveCounter": 0,
                "defect": False,
                "channels": {
                    "ch0000": {
                        "floor": "02",
                        "room": "02",
                        "displayName": "Ⓐ",
                        "functionID": "0",
                        "inputs": {
                            "idp0000": {"pairingID": 256, "value": "0"},
                            "idp0001": {"pairingID": 18, "value": "0"},
                            "idp0002": {"pairingID": 273, "value": "0"},
                            "idp0004": {"pairingID": 261, "value": "0"},
                            "idp0005": {"pairingID": 278, "value": "0"},
                        },
                        "outputs": {
                            "odp0000": {"pairingID": 1, "value": "0"},
                            "odp0006": {"pairingID": 4, "value": "0"},
                        },
                        "parameters": {
                            "par0002": "50",
                            "par0001": "50",
                            "par0007": "1",
                        },
                    },
                    "ch0003": {
                        "floor": "02",
                        "room": "02",
                        "displayName": "Ⓐ",
                        "selectedIcon": "01",
                        "functionID": "7",
                        "inputs": {
                            "idp0000": {"pairingID": 1, "value": "0"},
                            "idp0001": {"pairingID": 2, "value": "0"},
                            "idp0002": {"pairingID": 3, "value": "0"},
                            "idp0003": {"pairingID": 4, "value": "1"},
                            "idp0004": {"pairingID": 6, "value": "0"},
                        },
                        "outputs": {
                            "odp0000": {"pairingID": 256, "value": "0"},
                            "odp0001": {"pairingID": 257, "value": "0"},
                        },
                        "parameters": {"par0015": "360", "par0014": "1"},
                    },
                },
                "parameters": {"par00ed": "1"},
            },
            "BEED509C0001": {
                "floor": "01",
                "room": "01",
                "interface": "hue",
                "deviceId": "10C0",
                "displayName": "LED Strip",
                "unresponsive": False,
                "unresponsiveCounter": 0,
                "defect": False,
                "channels": {
                    "ch0000": {
                        "floor": "02",
                        "room": "06",
                        "displayName": "TV LED Strip Top",
                        "selectedIcon": "6a",
                        "functionID": "2e",
                        "inputs": {},
                        "outputs": {},
                        "parameters": {},
                    }
                },
                "parameters": {},
            },
        },
    }
    return api


@pytest.fixture
def freeathome(api_mock):
    """Create the FreeAtHome fixture."""
    return FreeAtHome(api=api_mock, interfaces=[Interface.WIRED_BUS])


@pytest.mark.asyncio
async def test_floors(freeathome):
    """Test the floors property."""
    floors = await freeathome.get_floors()
    assert floors == {
        "01": {
            "name": "Ground Floor",
            "rooms": {"01": {"name": "Living Room"}},
        },
        "02": {"name": "First Floor", "rooms": {"02": {"name": "Bedroom"}}},
    }


@pytest.mark.asyncio
async def test_get_config(freeathome, api_mock):
    """Test the get_config function."""
    config = await freeathome.get_config()
    assert config == api_mock.get_configuration.return_value
    api_mock.get_configuration.assert_called_once()


@pytest.mark.asyncio
async def test_get_devices_by_function(freeathome):
    """Test the get_devices_by_fuction function."""
    devices = await freeathome.get_devices_by_function(FunctionID.FID_SWITCH_ACTUATOR)
    assert len(devices) == 2
    assert devices[0]["device_name"] == "Study Area Rocker"
    assert devices[0]["channel_name"] == "Study Area Light"
    assert devices[0]["floor_name"] == "Ground Floor"
    assert devices[0]["room_name"] == "Living Room"


@pytest.mark.asyncio
async def test_get_floor_name(freeathome):
    """Test the get_floor_name function."""
    floor_name = await freeathome.get_floor_name("01")
    assert floor_name == "Ground Floor"

    floor_name = await freeathome.get_floor_name(floor_serial_id=None)
    assert floor_name is None


@pytest.mark.asyncio
async def test_get_room_name(freeathome):
    """Test the get_room_name function."""
    room_name = await freeathome.get_room_name("01", "01")
    assert room_name == "Living Room"

    room_name = await freeathome.get_room_name(
        floor_serial_id="01", room_serial_id=None
    )
    assert room_name is None

    room_name = await freeathome.get_room_name(
        floor_serial_id=None, room_serial_id=None
    )
    assert room_name is None

    room_name = await freeathome.get_room_name(
        floor_serial_id=None, room_serial_id="01"
    )
    assert room_name is None


def test_get_device_by_class(freeathome):
    """Test the get_device_class function."""
    device = MagicMock(spec=SwitchActuator)
    freeathome._devices = {"device1": device}
    devices = freeathome.get_device_by_class(SwitchActuator)
    assert devices == [device]


@pytest.mark.asyncio
async def test_load_devices(freeathome):
    """Test the load_devices function."""
    await freeathome.load_devices()

    # Verify that the devices are loaded correctly
    assert len(freeathome._devices) == 2
    device_key = "ABB7F500E17A/ch0003"
    assert device_key in freeathome._devices
    assert isinstance(freeathome._devices[device_key], SwitchActuator)
    assert freeathome._devices[device_key].device_name == "Study Area Rocker"
    assert freeathome._devices[device_key].channel_name == "Study Area Light"
    assert freeathome._devices[device_key].floor_name == "Ground Floor"
    assert freeathome._devices[device_key].room_name == "Living Room"


@pytest.mark.asyncio
async def test_ws_close(freeathome, api_mock):
    "Test the ws_close function."
    api_mock.ws_close = AsyncMock()
    await freeathome.ws_close()
    api_mock.ws_close.assert_called_once_with()


@pytest.mark.asyncio
async def test_ws_listen(freeathome, api_mock):
    "Test the ws_listen function."
    api_mock.ws_listen = AsyncMock()
    await freeathome.ws_listen()
    api_mock.ws_listen.assert_called_once_with(callback=freeathome.update_device)


@pytest.mark.asyncio
async def test_update_device(freeathome):
    """Test the update device function."""
    device = MagicMock()
    freeathome._devices = {"ABB7F500E17A/ch0003": device}
    data = {
        "datapoints": {"ABB7F500E17A/ch0003/256": "0", "ABB7F500E17A/ch0001/0": "0"}
    }
    await freeathome.update_device(data)
    device.update_device.assert_called_once_with("ABB7F500E17A/ch0003/256", "0")
