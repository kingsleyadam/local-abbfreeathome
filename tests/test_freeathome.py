"""Test code to test all FreeAtHome class."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.function import Function
from src.abbfreeathome.bin.interface import Interface
from src.abbfreeathome.devices.switch_actuator import SwitchActuator
from src.abbfreeathome.devices.switch_sensor import SwitchSensor
from src.abbfreeathome.devices.virtual.virtual_switch_actuator import (
    VirtualSwitchActuator,
)
from src.abbfreeathome.freeathome import FreeAtHome


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
            "ABB7F62F6A46": {
                "deviceReboots": "31",
                "floor": "01",
                "room": "18",
                "interface": "TP",
                "deviceId": "910C",
                "displayName": "Kitchen Rocker",
                "unresponsive": False,
                "unresponsiveCounter": 0,
                "defect": False,
                "channels": {
                    "ch0000": {
                        "floor": "01",
                        "room": "18",
                        "displayName": "Kitchen Light",
                        "functionID": "1",
                        "inputs": {
                            "idp0000": {"pairingID": 256, "value": "1"},
                            "idp0001": {"pairingID": 18, "value": "0"},
                            "idp0002": {"pairingID": 273, "value": "0"},
                            "idp0004": {"pairingID": 261, "value": "0"},
                            "idp0005": {"pairingID": 278, "value": "0"},
                            "idp0009": {"pairingID": 272, "value": "22"},
                            "idp000a": {"pairingID": 277, "value": "0"},
                        },
                        "outputs": {
                            "odp0000": {"pairingID": 1, "value": "1"},
                            "odp0001": {"pairingID": 16, "value": "8"},
                            "odp0006": {"pairingID": 4, "value": "0"},
                        },
                        "parameters": {
                            "par0002": "50",
                            "par0001": "50",
                            "par0007": "1",
                        },
                    },
                    "ch0003": {
                        "displayName": "Ⓐ",
                        "selectedIcon": "1",
                        "functionID": "7",
                        "inputs": {
                            "idp0000": {"pairingID": 1, "value": "0"},
                            "idp0001": {"pairingID": 2, "value": "0"},
                            "idp0002": {"pairingID": 3, "value": "0"},
                            "idp0003": {"pairingID": 4, "value": "0"},
                            "idp0004": {"pairingID": 6, "value": "0"},
                        },
                        "outputs": {
                            "odp0000": {"pairingID": 256, "value": "1"},
                            "odp0001": {"pairingID": 257, "value": "0"},
                        },
                        "parameters": {"par0015": "60", "par0014": "1"},
                    },
                },
                "parameters": {"par00ed": "1"},
            },
            "ABB28CBC3651": {
                "interface": "TP",
                "deviceId": "B008",
                "displayName": "Sensor/switch actuator",
                "unresponsive": False,
                "unresponsiveCounter": 0,
                "defect": False,
                "channels": {
                    "ch0006": {
                        "displayName": "Ⓐ",
                        "selectedIcon": "1e",
                        "functionID": "0",
                        "inputs": {"idp0000": {"pairingID": 256, "value": "0"}},
                        "outputs": {"odp0000": {"pairingID": 1, "value": "0"}},
                        "parameters": {"par0010": "1", "par0043": "1"},
                    },
                },
            },
            "60002AE2F1BE": {
                "nativeId": "abcd12350",
                "deviceId": "0004",
                "displayName": "MyVirtualDoorSensor",
                "unresponsive": False,
                "unresponsiveCounter": 0,
                "defect": False,
                "channels": {
                    "ch0000": {
                        "displayName": "MyVirtualDoorSensor",
                        "floor": "01",
                        "room": "01",
                        "functionID": "f",
                        "inputs": {},
                        "outputs": {"odp000c": {"pairingID": 53, "value": ""}},
                        "parameters": {"par0010": "1"},
                        "selectedIcon": "51",
                    }
                },
                "parameters": {},
            },
            "60005D808C54": {
                "floor": "01",
                "room": "01",
                "nativeId": "virtual-switch-sleep",
                "interface": "vdev:installer@busch-jaeger.de",
                "deviceId": "0001",
                "displayName": "Sleepmode",
                "unresponsive": False,
                "unresponsiveCounter": 0,
                "defect": False,
                "channels": {
                    "ch0000": {
                        "displayName": "Sleepmode",
                        "floor": "01",
                        "room": "01",
                        "functionID": "7",
                        "inputs": {
                            "idp0000": {"pairingID": 1, "value": "1"},
                            "idp0001": {"pairingID": 2, "value": ""},
                            "idp0002": {"pairingID": 3, "value": ""},
                            "idp0003": {"pairingID": 4, "value": ""},
                            "idp0004": {"pairingID": 6, "value": ""},
                        },
                        "outputs": {
                            "odp0000": {"pairingID": 256, "value": "0"},
                            "odp0001": {"pairingID": 257, "value": "0"},
                        },
                        "parameters": {"par0015": "60", "par0014": "1"},
                        "selectedIcon": "0B",
                    }
                },
                "parameters": {},
            },
            # this is a virtual device with no device-class associated
            "6000123456789": {
                "deviceReboots": "0",
                "floor": "01",
                "room": "01",
                "displayName": "Virtual Area Rocker",
                "unresponsive": False,
                "unresponsiveCounter": 0,
                "defect": False,
                "channels": {
                    "ch0000": {
                        "floor": "01",
                        "room": "01",
                        "displayName": "Virtual Area Rocker",
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
                },
                "parameters": {"par00ed": "1"},
            },
        },
    }
    return api


@pytest.fixture
def freeathome(api_mock):
    """Create the FreeAtHome fixture."""
    return FreeAtHome(
        api=api_mock,
        interfaces=[Interface.WIRED_BUS],
        include_orphan_channels=False,
    )


@pytest.fixture
def freeathome_orphans(api_mock):
    """Create the FreeAtHome fixture."""
    return FreeAtHome(
        api=api_mock,
        interfaces=[Interface.WIRED_BUS],
        include_orphan_channels=True,
    )


# This can be removed, when ABB fixes the bug
@pytest.fixture
def freeathome_virtuals(api_mock):
    """Create the FreeAtHome fixture."""
    return FreeAtHome(
        api=api_mock,
        interfaces=[Interface.VIRTUAL_DEVICE],
        include_orphan_channels=False,
    )


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
    devices = await freeathome.get_devices_by_function(Function.FID_SWITCH_ACTUATOR)
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


@pytest.mark.asyncio
async def test_get_device_by_class(freeathome):
    """Test the get_device_class function."""
    await freeathome.load_devices()

    devices = freeathome.get_devices_by_class(SwitchActuator)
    assert len(devices) == 2


@pytest.mark.asyncio
async def test_load_devices(freeathome):
    """Test the load_devices function."""
    await freeathome.load_devices()

    # Get the dict of devices
    devices = freeathome.get_devices()

    # Verify that the devices are loaded correctly
    assert len(devices) == 5

    # Check a single device
    device_key = "ABB7F500E17A/ch0003"
    assert device_key in devices
    assert isinstance(devices[device_key], SwitchActuator)
    assert devices[device_key].device_name == "Study Area Rocker"
    assert devices[device_key].channel_name == "Study Area Light"
    assert devices[device_key].floor_name == "Ground Floor"
    assert devices[device_key].room_name == "Living Room"
    assert devices[device_key].is_virtual is False

    # Unload a single device and test it's been removed
    freeathome.unload_device_by_device_serial(device_serial="ABB7F62F6C0B")
    devices = freeathome.get_devices()
    assert len(devices) == 3


@pytest.mark.asyncio
async def test_load_devices_with_orphans(freeathome_orphans):
    """Test the load_devices function."""
    await freeathome_orphans.load_devices()

    # Get the dict of devices
    devices = freeathome_orphans.get_devices()

    # Verify that the devices are loaded correctly
    assert len(devices) == 7

    # Check a single orphan device
    device_key = "ABB28CBC3651/ch0006"
    assert device_key in devices
    assert isinstance(devices[device_key], SwitchSensor)
    assert devices[device_key].device_name == "Sensor/switch actuator"
    assert devices[device_key].channel_name == "Sensor/switch actuator"
    assert devices[device_key].floor_name is None
    assert devices[device_key].room_name is None


@pytest.mark.asyncio
async def test_load_devices_with_virtuals(freeathome_virtuals):
    """Test the load_devices function."""
    await freeathome_virtuals.load_devices()

    # Get the dict of devices
    devices = freeathome_virtuals.get_devices()

    # Verify that the devices are loaded correctly
    assert len(devices) == 2

    # Check a single virtual device
    device_key = "60005D808C54/ch0000"
    assert device_key in devices
    assert isinstance(devices[device_key], VirtualSwitchActuator)
    assert devices[device_key].device_name == "Sleepmode"
    assert devices[device_key].channel_name == "Sleepmode"
    assert devices[device_key].floor_name == "Ground Floor"
    assert devices[device_key].room_name == "Living Room"
    assert devices[device_key].is_virtual is True


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
