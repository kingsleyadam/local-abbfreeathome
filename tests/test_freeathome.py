"""Test code to test all FreeAtHome class."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.interface import Interface
from src.abbfreeathome.channels.switch_actuator import SwitchActuator
from src.abbfreeathome.channels.switch_sensor import SwitchSensor
from src.abbfreeathome.channels.virtual.virtual_switch_actuator import (
    VirtualSwitchActuator,
)
from src.abbfreeathome.device import Device
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
async def test_get_config(freeathome, api_mock):
    """Test the get_config function."""
    config = await freeathome.get_config()
    assert config == api_mock.get_configuration.return_value
    api_mock.get_configuration.assert_called_once()


@pytest.mark.asyncio
async def test_get_config_with_refresh(api_mock):
    """Test the get_config function with refresh=True."""
    freeathome = FreeAtHome(api_mock)

    # First call to populate _config
    config1 = await freeathome.get_config()
    assert config1 == api_mock.get_configuration.return_value
    api_mock.get_configuration.assert_called_once()

    # Reset the mock call count
    api_mock.get_configuration.reset_mock()

    # Second call with refresh=True should call get_configuration again
    config2 = await freeathome.get_config(refresh=True)
    assert config2 == api_mock.get_configuration.return_value
    # Should be called again due to refresh=True
    api_mock.get_configuration.assert_called_once()


@pytest.mark.asyncio
async def test_get_config_cached(api_mock):
    """Test that get_config returns cached config when not refreshing."""
    freeathome = FreeAtHome(api_mock)

    # First call should fetch config
    config1 = await freeathome.get_config()
    assert config1 == api_mock.get_configuration.return_value
    api_mock.get_configuration.assert_called_once()

    # Reset the mock call count
    api_mock.get_configuration.reset_mock()

    # Second call without refresh should NOT call get_configuration again
    config2 = await freeathome.get_config()
    assert config2 == config1  # Should return cached config
    api_mock.get_configuration.assert_not_called()  # Should not be called again

    # Explicitly test with refresh=False
    config3 = await freeathome.get_config(refresh=False)
    assert config3 == config1  # Should return cached config
    api_mock.get_configuration.assert_not_called()  # Should still not be called


@pytest.mark.asyncio
async def test_get_channels_by_class(freeathome):
    """Test the get_channels_by_class function."""
    await freeathome.load()

    devices = freeathome.get_channels_by_class(SwitchActuator)
    assert len(devices) == 2


@pytest.mark.asyncio
async def test_get_channels_by_device(freeathome):
    """Test the get_channels_by_device function."""
    await freeathome.load()

    # Test getting channels for a specific device that has multiple channels
    channels_device1 = freeathome.get_channels_by_device("ABB7F500E17A")
    assert len(channels_device1) == 2  # Device has ch0000 and ch0003

    # Verify the channels belong to the correct device
    for channel in channels_device1:
        assert channel.device_serial == "ABB7F500E17A"

    # Test getting channels for another device
    channels_device2 = freeathome.get_channels_by_device("ABB7F62F6C0B")
    assert len(channels_device2) == 2  # Device has ch0000 and ch0003

    # Verify the channels belong to the correct device
    for channel in channels_device2:
        assert channel.device_serial == "ABB7F62F6C0B"

    # Test getting channels for a device with no channels (should return empty list)
    channels_empty = freeathome.get_channels_by_device("NONEXISTENT")
    assert len(channels_empty) == 0
    assert isinstance(channels_empty, list)

    # Test getting channels for a device that exists but may have filtered channels
    # BEED509C0001 has one channel but it might be filtered out due to room/floor
    # mismatch
    channels_filtered = freeathome.get_channels_by_device("BEED509C0001")
    # This should return 0 because the channel has floor "02"/room "06"
    # but device is floor "01"/room "01"
    assert len(channels_filtered) == 0


@pytest.mark.asyncio
async def test_load(freeathome):
    """Test the load function."""
    await freeathome.load()

    # Get the dict of channels
    channels = freeathome.get_channels()

    # Verify that the channels are loaded correctly
    assert len(channels) == 5

    # Check a single channel
    channel_key = "ABB7F500E17A/ch0003"
    assert channel_key in channels
    assert isinstance(channels[channel_key], SwitchActuator)
    assert channels[channel_key].device_name == "Study Area Rocker"
    assert channels[channel_key].channel_name == "Study Area Light"
    assert channels[channel_key].floor_name == "Ground Floor"
    assert channels[channel_key].room_name == "Living Room"
    assert channels[channel_key].is_virtual is False

    # Unload a single channel and test it's been removed
    freeathome.unload_channel(
        device_serial=channels[channel_key].device.device_serial,
        channel_id=channels[channel_key].channel_id,
    )
    channels = freeathome.get_channels()
    assert len(channels) == 4


@pytest.mark.asyncio
async def test_load_with_orphans(freeathome_orphans):
    """Test the load function."""
    await freeathome_orphans.load()

    # Get the dict of channels
    channels = freeathome_orphans.get_channels()

    # Verify that the channels are loaded correctly
    assert len(channels) == 7

    # Check a single orphan channel
    channel_key = "ABB28CBC3651/ch0006"
    assert channel_key in channels
    assert isinstance(channels[channel_key], SwitchSensor)
    assert channels[channel_key].device_name == "Sensor/switch actuator"
    assert channels[channel_key].channel_name == "Sensor/switch actuator"
    assert channels[channel_key].floor_name is None
    assert channels[channel_key].room_name is None


@pytest.mark.asyncio
async def test_load_with_virtuals(freeathome_virtuals):
    """Test the load function."""
    await freeathome_virtuals.load()

    # Get the dict of channels
    channels = freeathome_virtuals.get_channels()

    # Verify that the channels are loaded correctly
    assert len(channels) == 2

    # Check a single virtual channel
    channel_key = "60005D808C54/ch0000"
    assert channel_key in channels
    assert isinstance(channels[channel_key], VirtualSwitchActuator)
    assert channels[channel_key].device_name == "Sleepmode"
    assert channels[channel_key].channel_name == "Sleepmode"
    assert channels[channel_key].floor_name == "Ground Floor"
    assert channels[channel_key].room_name == "Living Room"
    assert channels[channel_key].is_virtual is True


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
    api_mock.ws_listen.assert_called_once_with(callback=freeathome.update)


@pytest.mark.asyncio
async def test_update(freeathome):
    """Test the update function."""
    # Create a mock channel
    channel = MagicMock()

    # Create a device with the channel that has floor/room info to pass orphan filtering
    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        interface=Interface.WIRED_BUS,
        channels_data={
            "ch0003": {"functionID": "0", "floor": "floor1", "room": "room1"}
        },
        api=freeathome.api,
    )

    # Add the device to freeathome
    freeathome._devices["ABB7F500E17A"] = device

    # Mock the device.channels to return our mock channel
    device._channels = {"ch0003": channel}

    data = {
        "datapoints": {"ABB7F500E17A/ch0003/256": "0", "ABB7F500E17A/ch0001/0": "0"}
    }
    await freeathome.update(data)
    channel.update_channel.assert_called_once_with("ABB7F500E17A/ch0003/256", "0")


@pytest.mark.asyncio
async def test_device_interface_enum_conversion(api_mock):
    """Test that interface strings are properly converted to Interface enums."""
    api_mock.get_configuration = AsyncMock(
        return_value={
            "devices": {
                "ABB7F500E17A": {
                    "deviceId": "910C",
                    "displayName": "Test TP Device",
                    "interface": "TP",
                    "unresponsive": False,
                    "unresponsiveCounter": 0,
                    "defect": False,
                    "channels": {},
                },
                "BEED509C0001": {
                    "deviceId": "10C0",
                    "displayName": "Test HUE Device",
                    "interface": "hue",
                    "unresponsive": False,
                    "unresponsiveCounter": 0,
                    "defect": False,
                    "channels": {},
                },
                "6000F91624D1": {
                    "deviceId": "0161",
                    "displayName": "Test Virtual Device",
                    "interface": "vdev:script.test",
                    "unresponsive": False,
                    "unresponsiveCounter": 0,
                    "defect": False,
                    "channels": {},
                },
            },
            "floorplan": {"floors": {}},
        }
    )

    freeathome = FreeAtHome(api_mock)
    await freeathome._load_devices()

    devices = freeathome.get_devices()

    # Test TP device interface conversion
    tp_device = devices["ABB7F500E17A"]
    assert tp_device.interface == Interface.WIRED_BUS
    assert tp_device.interface.value == "TP"

    # Test HUE device interface conversion
    hue_device = devices["BEED509C0001"]
    assert hue_device.interface == Interface.HUE
    assert hue_device.interface.value == "hue"

    # Test virtual device interface conversion
    virtual_device = devices["6000F91624D1"]
    assert virtual_device.interface == Interface.VIRTUAL_DEVICE
    assert virtual_device.interface.value == "VD"
    assert virtual_device.is_virtual is True


@pytest.mark.asyncio
async def test_load_devices_functionality(api_mock):
    """Test the load_devices method and device-related functionality."""
    freeathome = FreeAtHome(api_mock)

    # Test initial state
    assert len(freeathome.get_devices()) == 0

    # Load devices
    await freeathome._load_devices()
    devices = freeathome.get_devices()

    # Test that devices are loaded
    assert len(devices) > 0

    # Test get_device_by_serial
    device = freeathome.get_device_by_serial("ABB7F500E17A")
    assert device is not None
    assert device.device_serial == "ABB7F500E17A"
    assert device.display_name == "Study Area Rocker"
    assert device.interface == Interface.WIRED_BUS

    # Test non-existent device
    non_existent = freeathome.get_device_by_serial("NONEXISTENT")
    assert non_existent is None

    # Test clear_devices
    freeathome.clear_devices()
    assert len(freeathome.get_devices()) == 0


@pytest.mark.asyncio
async def test_unload_device(api_mock):
    """Test unloading devices by serial."""
    freeathome = FreeAtHome(api_mock)
    await freeathome._load_devices()

    initial_count = len(freeathome.get_devices())
    assert initial_count > 0

    # Unload a specific device
    freeathome.unload_device("ABB7F500E17A")

    # Verify device was removed
    assert len(freeathome.get_devices()) == initial_count - 1
    assert freeathome.get_device_by_serial("ABB7F500E17A") is None

    # Test unloading non-existent device (should not raise error)
    freeathome.unload_device("NONEXISTENT")
    assert len(freeathome.get_devices()) == initial_count - 1


@pytest.mark.asyncio
async def test_interface_conversion_mapping(api_mock):
    """Test the interface string to enum conversion mapping."""
    # Create a custom API mock with specific interface types
    api_mock.get_configuration = AsyncMock(
        return_value={
            "devices": {
                "TP_DEVICE": {
                    "deviceId": "910C",
                    "displayName": "TP Device",
                    "interface": "TP",
                    "unresponsive": False,
                    "unresponsiveCounter": 0,
                    "defect": False,
                    "channels": {},
                },
                "RF_DEVICE": {
                    "deviceId": "910D",
                    "displayName": "RF Device",
                    "interface": "RF",
                    "unresponsive": False,
                    "unresponsiveCounter": 0,
                    "defect": False,
                    "channels": {},
                },
                "HUE_DEVICE": {
                    "deviceId": "10C0",
                    "displayName": "HUE Device",
                    "interface": "hue",
                    "unresponsive": False,
                    "unresponsiveCounter": 0,
                    "defect": False,
                    "channels": {},
                },
                "SONOS_DEVICE": {
                    "deviceId": "0001",
                    "displayName": "SONOS Device",
                    "interface": "sonos",
                    "unresponsive": False,
                    "unresponsiveCounter": 0,
                    "defect": False,
                    "channels": {},
                },
                "SMOKEALARM_DEVICE": {
                    "deviceId": "B001",
                    "displayName": "Smoke Alarm Device",
                    "interface": "smokealarm",
                    "unresponsive": False,
                    "unresponsiveCounter": 0,
                    "defect": False,
                    "channels": {},
                },
                "VDEV_DEVICE": {
                    "deviceId": "0161",
                    "displayName": "Virtual Device",
                    "interface": "vdev:test.example",
                    "unresponsive": False,
                    "unresponsiveCounter": 0,
                    "defect": False,
                    "channels": {},
                },
                "VD_DEVICE": {
                    "deviceId": "0001",
                    "displayName": "VD Device",
                    "interface": "VD",
                    "unresponsive": False,
                    "unresponsiveCounter": 0,
                    "defect": False,
                    "channels": {},
                },
                "UNKNOWN_DEVICE": {
                    "deviceId": "UNKNOWN",
                    "displayName": "Unknown Device",
                    "interface": "unknown_interface",
                    "unresponsive": False,
                    "unresponsiveCounter": 0,
                    "defect": False,
                    "channels": {},
                },
                "NO_INTERFACE_DEVICE": {
                    "deviceId": "NONE",
                    "displayName": "No Interface Device",
                    "unresponsive": False,
                    "unresponsiveCounter": 0,
                    "defect": False,
                    "channels": {},
                },
            },
            "floorplan": {"floors": {}},
        }
    )

    freeathome = FreeAtHome(api_mock)
    await freeathome._load_devices()
    devices = freeathome.get_devices()

    # Test interface conversions
    expected_mappings = [
        ("TP_DEVICE", Interface.WIRED_BUS),
        ("RF_DEVICE", Interface.WIRELESS_RF),
        ("HUE_DEVICE", Interface.HUE),
        ("SONOS_DEVICE", Interface.SONOS),
        ("SMOKEALARM_DEVICE", Interface.SMOKEALARM),
        ("VD_DEVICE", Interface.VIRTUAL_DEVICE),
        ("UNKNOWN_DEVICE", Interface.UNDEFINED),  # Unknown interface maps to UNDEFINED
        ("NO_INTERFACE_DEVICE", Interface.UNDEFINED),  # No interface maps to UNDEFINED
    ]

    for device_serial, expected_interface in expected_mappings:
        device = devices[device_serial]
        assert device.interface == expected_interface, (
            f"Device {device_serial} should have interface {expected_interface}, "
            f"got {device.interface}"
        )


@pytest.mark.asyncio
async def test_device_floor_room_names(api_mock):
    """Test that device floor and room names are properly populated."""
    freeathome = FreeAtHome(api_mock)
    await freeathome._load_devices()
    devices = freeathome.get_devices()

    # Test device with floor and room
    device_with_location = devices["ABB7F500E17A"]
    assert device_with_location.floor == "01"
    assert device_with_location.room == "01"
    assert device_with_location.floor_name == "Ground Floor"
    assert device_with_location.room_name == "Living Room"

    # Test device with different floor and room
    bedroom_device = devices["ABB7F62F6C0B"]
    assert bedroom_device.floor == "02"
    assert bedroom_device.room == "02"
    assert bedroom_device.floor_name == "First Floor"
    assert bedroom_device.room_name == "Bedroom"

    # Test device without floor/room (should have None values)
    no_location_device = devices["ABB28CBC3651"]
    assert no_location_device.floor is None
    assert no_location_device.room is None
    assert no_location_device.floor_name is None
    assert no_location_device.room_name is None


@pytest.mark.asyncio
async def test_clear_channels(api_mock):
    """Test the clear_channels method."""
    freeathome = FreeAtHome(api_mock)

    # Load some devices first
    await freeathome.load()

    # Verify devices have channels
    devices = freeathome.get_devices()
    assert len(devices) > 0

    # Clear channels
    freeathome.clear_channels()

    # Verify all device channels are cleared and filtered cache is invalidated
    for device in devices.values():
        if hasattr(device, "_channels"):
            assert device._channels == {}
    assert freeathome._filtered_channels is None


@pytest.mark.asyncio
async def test_channel_class_filtering(api_mock):
    """Test filtering channels by channel class."""
    # Initialize FreeAtHome with specific channel class filter
    freeathome = FreeAtHome(
        api_mock,
        channel_classes=[SwitchActuator],  # Only SwitchActuator
    )

    await freeathome.load()

    # Get filtered channels
    channels = freeathome.get_channels()

    # Verify all returned channels are of the specified class
    for channel in channels.values():
        assert isinstance(channel, SwitchActuator)


@pytest.mark.asyncio
async def test_unload_channel_by_id(api_mock):
    """Test unloading specific channels by channel serial."""
    freeathome = FreeAtHome(api_mock)
    await freeathome.load()

    initial_channels = freeathome.get_channels()
    initial_count = len(initial_channels)
    assert initial_count > 0

    # Test unloading a specific channel using channel serial format
    channel_serial = "ABB7F500E17A/ch0003"
    assert channel_serial in initial_channels

    channel = initial_channels["ABB7F500E17A/ch0003"]
    freeathome.unload_channel(
        device_serial=channel.device.device_serial, channel_id=channel.channel_id
    )

    # Verify the specific channel was removed
    updated_channels = freeathome.get_channels()
    assert channel_serial not in updated_channels
    assert len(updated_channels) == initial_count - 1


@pytest.mark.asyncio
async def test_unload_channel_invalid_serial(api_mock):
    """Test unloading channel with invalid channel serial."""
    freeathome = FreeAtHome(api_mock)
    await freeathome.load()

    initial_channels = freeathome.get_channels()
    initial_count = len(initial_channels)

    # Test with invalid device serial
    freeathome.unload_channel(device_serial="NONEXISTENT", channel_id="ch0000")

    # Should not change anything
    updated_channels = freeathome.get_channels()
    assert len(updated_channels) == initial_count

    # Test with invalid channel_id
    freeathome.unload_channel(device_serial="ABB7F500E17A", channel_id="NONEXISTENT")

    # Should not change anything
    updated_channels = freeathome.get_channels()
    assert len(updated_channels) == initial_count
