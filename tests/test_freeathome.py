"""Test code to test all FreeAtHome class."""

from copy import deepcopy
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.interface import Interface
from src.abbfreeathome.bin.pairing import Pairing
from src.abbfreeathome.channels.switch_actuator import SwitchActuator
from src.abbfreeathome.channels.switch_sensor import SwitchSensor
from src.abbfreeathome.channels.virtual.virtual_switch_actuator import (
    VirtualSwitchActuator,
)
from src.abbfreeathome.device import Device
from src.abbfreeathome.floorplan import Floorplan
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

    # Steady-state: the api is not in the priming window.
    freeathome.api.is_priming = False

    data = {
        "datapoints": {"ABB7F500E17A/ch0003/256": "0", "ABB7F500E17A/ch0001/0": "0"}
    }
    await freeathome.update(data)
    channel.update_channel.assert_called_once_with(
        "ABB7F500E17A/ch0003/256", "0", is_priming=False
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("is_priming", [False, True])
@pytest.mark.parametrize(("initial_value", "value"), [("0", "1"), ("1", "0")])
async def test_update_scene_virtual_switch(
    freeathome_virtuals, api_mock, is_priming, initial_value, value
):
    """Test scene outputs update state and emit a virtual switch request."""
    serial = "6000D2CB27B2"
    devices = api_mock.get_configuration.return_value["devices"]
    devices[serial] = devices.pop("60005D808C54")
    devices[serial]["channels"]["ch0000"]["outputs"]["odp0000"]["value"] = initial_value
    await freeathome_virtuals.load()
    channel = freeathome_virtuals.get_channels()[f"{serial}/ch0000"]
    callback = MagicMock()
    channel.register_callback(callback_attribute="state", callback=callback)
    request_callback = MagicMock()
    channel.register_callback(
        callback_attribute="requested_state", callback=request_callback
    )
    api_mock.is_priming = is_priming
    data = {
        "datapoints": {f"{serial}/ch0000/idp0003": "4"},
        "parameters": {},
        "devices": {},
        "devicesAdded": [],
        "devicesRemoved": [],
        "scenesTriggered": {
            serial: {
                "channels": {
                    "ch0000": {
                        "outputs": {"odp0000": {"value": value, "pairingID": 256}}
                    }
                }
            }
        },
    }

    await freeathome_virtuals.update(data)

    assert channel.state is (value == "1")
    assert channel._outputs["odp0000"]["value"] == value
    assert channel._inputs["idp0003"]["value"] == "4"
    callback.assert_called_once_with()
    assert channel.requested_state is (value == "1")
    request_callback.assert_called_once_with()
    api_mock.set_datapoint.assert_not_called()


@pytest.mark.asyncio
async def test_update_scene_duplicate_datapoint(freeathome_virtuals, api_mock):
    """Test an output present in both sections only notifies the channel once."""
    await freeathome_virtuals.load()
    channel = freeathome_virtuals.get_channels()["60005D808C54/ch0000"]
    callback = MagicMock()
    channel.register_callback(callback_attribute="state", callback=callback)
    request_callback = MagicMock()
    channel.register_callback("requested_state", request_callback)
    api_mock.is_priming = False
    data = {
        "datapoints": {"60005D808C54/ch0000/odp0000": "1"},
        "scenesTriggered": {
            "60005D808C54": {
                "channels": {
                    "ch0000": {"outputs": {"odp0000": {"value": "1", "pairingID": 256}}}
                }
            }
        },
    }

    original_data = deepcopy(data)
    await freeathome_virtuals.update(data)

    assert channel.state is True
    callback.assert_called_once_with()
    request_callback.assert_called_once_with()
    assert data == original_data


@pytest.mark.asyncio
@pytest.mark.parametrize("is_priming", [False, True])
async def test_update_scene_unchanged_output(freeathome_virtuals, api_mock, is_priming):
    """Test scene outputs preserve the existing priming callback behavior."""
    await freeathome_virtuals.load()
    channel = freeathome_virtuals.get_channels()["60005D808C54/ch0000"]
    callback = MagicMock()
    channel.register_callback(callback_attribute="state", callback=callback)
    api_mock.is_priming = is_priming

    await freeathome_virtuals.update(
        {
            "scenesTriggered": {
                "60005D808C54": {
                    "channels": {
                        "ch0000": {
                            "outputs": {"odp0000": {"value": "0", "pairingID": 256}}
                        }
                    }
                }
            }
        }
    )

    assert channel.state is False
    if is_priming:
        callback.assert_not_called()
    else:
        callback.assert_called_once_with()


@pytest.mark.asyncio
async def test_update_scene_without_datapoints(freeathome_virtuals, api_mock):
    """Test scene-only updates skip unknown channels and empty scene sections."""
    await freeathome_virtuals.load()
    channel = freeathome_virtuals.get_channels()["60005D808C54/ch0000"]
    callback = MagicMock()
    channel.register_callback(callback_attribute="state", callback=callback)
    api_mock.is_priming = False
    output = {"outputs": {"odp0000": {"value": "1", "pairingID": 256}}}
    data = {
        "scenesTriggered": {
            "unknown": {"channels": {"ch0000": output}},
            "60005D808C54": {
                "channels": {"ch9999": output, "ch0001": {}, "ch0000": output}
            },
            "empty": {},
        }
    }

    await freeathome_virtuals.update(data)

    assert channel.state is True
    callback.assert_called_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize("data", [{}, {"scenesTriggered": {}}])
async def test_update_empty_data(freeathome_virtuals, data):
    """Test updates without datapoints or scene outputs are ignored."""
    await freeathome_virtuals.load()
    await freeathome_virtuals.update(data)


@pytest.mark.asyncio
async def test_update_scene_physical_switch(freeathome, api_mock):
    """Test physical channels still receive scene output state updates."""
    await freeathome.load()
    channel = freeathome.get_channels()["ABB7F500E17A/ch0003"]
    callback = MagicMock()
    channel.register_callback("state", callback)
    api_mock.is_priming = False

    await freeathome.update(
        {
            "scenesTriggered": {
                "ABB7F500E17A": {
                    "channels": {
                        "ch0003": {
                            "outputs": {"odp0000": {"value": "1", "pairingID": 256}}
                        }
                    }
                }
            }
        }
    )

    assert channel.state is True
    callback.assert_called_once_with()


@pytest.mark.asyncio
async def test_update_scene_multiple_virtual_switches(freeathome_virtuals, api_mock):
    """Test both reported devices emit requests and output echoes emit none."""
    serials = ("600061C8C3F9", "6000D2CB27B2")
    devices = api_mock.get_configuration.return_value["devices"]
    device = devices.pop("60005D808C54")
    for serial in serials:
        devices[serial] = deepcopy(device)
    await freeathome_virtuals.load()
    api_mock.is_priming = False
    events = {serial: [] for serial in serials}
    channels = freeathome_virtuals.get_channels()
    for serial in serials:
        channel = channels[f"{serial}/ch0000"]
        channel.register_callback(
            "requested_state",
            lambda serial=serial, channel=channel: events[serial].append(
                channel.requested_state
            ),
        )

    for value in ("1", "1", "0"):
        await freeathome_virtuals.update(
            {
                "datapoints": {f"{serial}/ch0000/idp0003": "4" for serial in serials},
                "scenesTriggered": {
                    serial: {
                        "channels": {
                            "ch0000": {
                                "outputs": {
                                    "odp0000": {"value": value, "pairingID": 256}
                                }
                            }
                        }
                    }
                    for serial in serials
                },
            }
        )
        # The automation confirms the virtual output through the API. Its
        # subsequent websocket echo must not trigger another switch request.
        await freeathome_virtuals.update(
            {"datapoints": {f"{serial}/ch0000/odp0000": value for serial in serials}}
        )

    assert events == {serial: [True, True, False] for serial in serials}
    api_mock.set_datapoint.assert_not_called()


@pytest.mark.asyncio
async def test_update_priming_suppresses_noop_callback_flood(freeathome, api_mock):
    """
    Regression for #239: a no-op snapshot replay during priming is silent.

    When the api reports it is priming (just after a websocket (re)connect), a
    replayed datapoint whose value is unchanged must update the cache but NOT
    fan out callbacks, preventing the phantom "button press" flood.
    """
    await freeathome.load()

    _channel = freeathome.get_channels()["ABB7F500E17A/ch0000"]
    _callback = MagicMock()
    _channel.register_callback(callback_attribute="state", callback=_callback)

    # The loaded cache for odp0000 is "0". Replaying the SAME value during
    # priming is a no-op and must be suppressed.
    assert _channel._outputs["odp0000"]["value"] == "0"
    api_mock.is_priming = True
    await freeathome.update({"datapoints": {"ABB7F500E17A/ch0000/odp0000": "0"}})

    _callback.assert_not_called()
    assert _channel._outputs["odp0000"]["value"] == "0"


@pytest.mark.asyncio
async def test_update_priming_fires_for_changed_value(freeathome, api_mock):
    """
    Regression for #239: a value changed during the outage still fires.

    A datapoint that genuinely changed while the socket was down must fire a
    callback even during the priming window. Suppress-no-ops only swallows
    unchanged datapoints, so changed values surface and consumers do not stay
    stale after a reconnect.
    """
    await freeathome.load()

    _channel = freeathome.get_channels()["ABB7F500E17A/ch0000"]
    _callback = MagicMock()
    _channel.register_callback(callback_attribute="state", callback=_callback)

    # Cache is "0"; a snapshot value of "1" is a real change -> callback fires.
    api_mock.is_priming = True
    await freeathome.update({"datapoints": {"ABB7F500E17A/ch0000/odp0000": "1"}})

    _callback.assert_called_once()
    assert _channel._outputs["odp0000"]["value"] == "1"
    assert _channel.state == "on"


@pytest.mark.asyncio
async def test_update_after_priming_fires_on_while_on(freeathome, api_mock):
    """
    Regression for #239: once priming ends, real events still fire callbacks.

    Crucially this includes an "on-while-on" event (a datapoint re-sent at its
    current value), which the maintainer wants to keep delivering.
    """
    await freeathome.load()

    _channel = freeathome.get_channels()["ABB7F500E17A/ch0000"]
    _callback = MagicMock()
    _channel.register_callback(callback_attribute="state", callback=_callback)

    # Put the channel into a known "on" state (not priming yet; one callback).
    api_mock.is_priming = False
    await freeathome.update({"datapoints": {"ABB7F500E17A/ch0000/odp0000": "1"}})
    assert _callback.call_count == 1

    # Re-send the SAME value: an on-while-on press must still fire a callback.
    await freeathome.update({"datapoints": {"ABB7F500E17A/ch0000/odp0000": "1"}})
    assert _callback.call_count == 2


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


def _params_freeathome(freeathome):
    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        interface=Interface.WIRED_BUS,
        parameters={"par00ed": "1"},
        channels_data={
            "ch0000": {
                "functionID": "0007",
                "floor": "01",
                "room": "01",
                "parameters": {"par0002": "50"},
            }
        },
        api=freeathome.api,
    )
    device.load_channels(floorplan=Floorplan())
    freeathome._devices["ABB7F500E17A"] = device
    return device, device.channels["ch0000"]


@pytest.mark.asyncio
async def test_update_parameters_from_devices(freeathome):
    """Parameter changes in the websocket `devices` payload fire callbacks."""
    device, channel = _params_freeathome(freeathome)
    channel_cb, device_cb = MagicMock(), MagicMock()
    channel.register_parameter_callback(channel_cb)
    device.register_parameter_callback(device_cb)

    data = {
        "devices": {
            "ABB7F500E17A": {
                "parameters": {"par00ed": "2"},
                "channels": {"ch0000": {"parameters": {"par0002": "60"}}},
            },
            "UNKNOWN": {"parameters": {"par0001": "1"}},
        }
    }
    await freeathome.update(data)

    assert channel.get_parameter("par0002") == "60"
    assert device.get_parameter(0xED) == "2"
    channel_cb.assert_called_once()
    device_cb.assert_called_once()

    # Unchanged values do not fire again
    await freeathome.update(data)
    channel_cb.assert_called_once()
    device_cb.assert_called_once()


@pytest.mark.asyncio
async def test_update_parameters_from_parameters_map(freeathome):
    """Parameter changes in the top-level `parameters` payload are applied."""
    device, channel = _params_freeathome(freeathome)
    filtered_cb, other_cb = MagicMock(), MagicMock()
    channel.register_parameter_callback(filtered_cb, parameter_id="par0002")
    channel.register_parameter_callback(other_cb, parameter_id=0x99)

    await freeathome.update(
        {
            "parameters": {
                "ABB7F500E17A/ch0000/par0002": "70",
                "ABB7F500E17A/par00ed": "3",
                "ABB7F500E17A/ch0009/par0002": "1",
                "NOPE/par0001": "1",
            }
        }
    )

    assert channel.parameters == {"par0002": "70"}
    assert device.parameters == {"par00ed": "3"}
    filtered_cb.assert_called_once()
    other_cb.assert_not_called()

    channel.remove_parameter_callback(filtered_cb, parameter_id="par0002")
    await freeathome.update({"parameters": {"ABB7F500E17A/ch0000/par0002": "80"}})
    filtered_cb.assert_called_once()


@pytest.mark.asyncio
async def test_update_parameters_from_devices_skips_unknown_channels(freeathome):
    """Unknown channels and malformed payloads in `devices` are ignored."""
    device, channel = _params_freeathome(freeathome)

    await freeathome.update(
        {
            "devices": {
                "ABB7F500E17A": {
                    "channels": {
                        "ch0009": {"parameters": {"par0002": "1"}},
                        "ch0000": "invalid",
                    }
                },
                "ABB7F500E17B": "invalid",
            }
        }
    )

    assert channel.parameters == {"par0002": "50"}
    assert device.parameters == {"par00ed": "1"}


@pytest.mark.asyncio
async def test_update_applies_parameters_before_datapoints(freeathome):
    """A parameter change is in effect for datapoints in the same message."""
    api = freeathome.api
    api.is_priming = False
    device = Device(
        device_serial="ABB7F500E17A",
        device_id="910C",
        display_name="Test Device",
        interface=Interface.WIRED_BUS,
        channels_data={
            "ch0000": {
                "functionID": "0000",
                "floor": "01",
                "room": "01",
                "outputs": {"odp0000": {"pairingID": 256, "value": "0"}},
                "parameters": {"par0007": "1"},
            }
        },
        api=api,
    )
    device.load_channels(floorplan=Floorplan())
    freeathome._devices["ABB7F500E17A"] = device
    channel = device.channels["ch0000"]
    led_callback = MagicMock()
    channel.register_callback("led", led_callback)

    await freeathome.update(
        {
            "parameters": {"ABB7F500E17A/ch0000/par0007": "2"},
            "datapoints": {"ABB7F500E17A/ch0000/odp0000": "1"},
        }
    )

    assert channel.led is True
    led_callback.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_priming", [False, True])
@pytest.mark.parametrize(
    ("serial", "source", "channel_id", "channel_class"),
    [
        ("ABB000000001", "ABB7F500E17A", "ch0003", SwitchActuator),
        ("600000000001", "60005D808C54", "ch0000", VirtualSwitchActuator),
    ],
)
async def test_device_addition_initializes_before_discovery(
    api_mock, serial, source, channel_id, channel_class, is_priming
):
    """Add devices atomically and notify after same-message state updates."""
    api_mock.is_priming = is_priming
    freeathome = FreeAtHome(api_mock)
    await freeathome.load()
    previous_devices = dict(freeathome.get_devices())
    previous_channels = dict(freeathome.get_channels())
    existing = previous_channels["ABB7F500E17A/ch0003"]
    existing_callback = MagicMock()
    existing.register_callback("state", existing_callback)
    device_data = deepcopy(api_mock.get_configuration.return_value["devices"][source])
    snapshots = []

    def discovered():
        device = freeathome.get_device_by_serial(serial)
        channel = freeathome.get_channels()[f"{serial}/{channel_id}"]
        snapshots.append((device, channel, channel.state, channel.get_parameter(0x15)))

    freeathome.register_devices_changed_callback(discovered)
    freeathome.register_devices_changed_callback(discovered)
    data = {
        "devicesAdded": [serial, serial],
        "devices": {serial: device_data},
        "parameters": {f"{serial}/{channel_id}/par0015": "90"},
        "datapoints": {
            "ABB7F500E17A/ch0003/odp0000": "1",
            f"{serial}/{channel_id}/odp0000": "0",
        },
        "scenesTriggered": {
            serial: {"channels": {channel_id: {"outputs": {"odp0000": {"value": "1"}}}}}
        },
    }
    original_data = deepcopy(data)
    await freeathome.update(data)

    device = freeathome.get_device_by_serial(serial)
    channel = device.channels[channel_id]
    assert snapshots == [(device, channel, True, "90")]
    assert type(channel) is channel_class
    assert channel.device is device
    assert channel.floor_name == "Ground Floor"
    assert channel.room_name == "Living Room"
    assert channel.is_virtual is serial.startswith("6000")
    if channel.is_virtual:
        assert channel.requested_state is True
    assert all(
        freeathome.get_devices()[key] is value
        for key, value in previous_devices.items()
    )
    assert all(
        freeathome.get_channels()[key] is value
        for key, value in previous_channels.items()
    )
    existing_callback.assert_called_once()
    config = await freeathome.get_config()
    assert (
        config["devices"][serial]["channels"][channel_id]["outputs"]["odp0000"]["value"]
        == "1"
    )
    assert (
        config["devices"][serial]["channels"][channel_id]["parameters"]["par0015"]
        == "90"
    )
    assert data == original_data
    api_mock.get_configuration.assert_awaited_once()
    api_mock.get_datapoint.assert_not_awaited()

    state_callback = MagicMock()
    channel.register_callback("state", state_callback)
    await freeathome.update(deepcopy(data))
    assert len(snapshots) == 1
    assert freeathome.get_device_by_serial(serial) is device
    assert freeathome.get_channels()[f"{serial}/{channel_id}"] is channel
    assert state_callback.call_count == int(not is_priming)

    freeathome.remove_devices_changed_callback(discovered)
    freeathome.remove_devices_changed_callback(discovered)
    await freeathome.update(
        {"devicesAdded": [f"{serial}2"], "devices": {f"{serial}2": device_data}}
    )
    assert len(snapshots) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("include_orphans", [False, True])
@pytest.mark.parametrize("parent_location", [False, True])
async def test_discovery_after_orphan_placement(
    api_mock, include_orphans, parent_location
):
    """Placement updates views and names without losing state or subscriptions."""
    api_mock.is_priming = False
    freeathome = FreeAtHome(api_mock, include_orphan_channels=include_orphans)
    await freeathome.load()
    serial = "ABB000000001"
    device_data = deepcopy(
        api_mock.get_configuration.return_value["devices"]["ABB7F500E17A"]
    )
    for source in [device_data, *device_data["channels"].values()]:
        source.pop("floor")
        source.pop("room")
    discovery = MagicMock()
    freeathome.register_devices_changed_callback(discovery)
    await freeathome.update(
        {"devicesAdded": [serial], "devices": {serial: device_data}}
    )
    discovery.assert_called_once()
    discovery.reset_mock()
    device = freeathome.get_device_by_serial(serial)
    channel = device.channels["ch0003"]
    channel_callback = MagicMock()
    channel.register_callback("state", channel_callback)
    device_parameter_callback = MagicMock()
    device.register_parameter_callback(device_parameter_callback)

    api_mock.get_configuration.return_value = deepcopy(await freeathome.get_config())
    await freeathome.get_config(refresh=True)
    snapshots = []

    def discovered():
        snapshots.append((channel.state, channel.floor_name, channel.room_name))

    freeathome.register_devices_changed_callback(discovered)
    data = {
        "devices": {
            serial: {
                "floor": "02",
                "room": "02",
                "parameters": {"par00ed": "2"},
                "channels": {
                    "ch0003": {
                        "floor": "02",
                        "room": "02",
                        "outputs": {"odp0000": {"pairingID": 256, "value": "1"}},
                    },
                    "unknown": {"floor": "02", "room": "02"},
                },
            }
        }
    }
    if not parent_location:
        data["devices"][serial].pop("floor")
        data["devices"][serial].pop("room")
    if include_orphans:
        data["datapoints"] = {f"{serial}/ch0003/odp0000": "1"}
    await freeathome.update(data)

    assert freeathome.get_device_by_serial(serial) is device
    assert freeathome.get_channels()[f"{serial}/ch0003"] is channel
    assert (device.floor, device.room) == (
        ("02", "02") if parent_location else (None, None)
    )
    assert (channel.floor_name, channel.room_name) == ("First Floor", "Bedroom")
    assert device.channels["ch0000"].room_name == (
        "Bedroom" if parent_location else None
    )
    channel_callback.assert_called_once()
    device_parameter_callback.assert_called_once()
    assert discovery.call_count == (0 if include_orphans else 1)
    assert snapshots == ([] if include_orphans else [(True, "First Floor", "Bedroom")])
    config = await freeathome.get_config()
    assert config["devices"][serial].get("floor") == ("02" if parent_location else None)
    assert config["devices"][serial]["channels"]["ch0003"]["room"] == "02"
    cached_channels = freeathome.get_channels()
    await freeathome.update(data)
    assert freeathome.get_channels() is cached_channels
    assert discovery.call_count == (0 if include_orphans else 1)
    assert "unknown" not in device.channels_data


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("interfaces", "classes", "source", "orphan", "loaded", "visible"),
    [
        ([Interface.WIRED_BUS], None, "60005D808C54", False, False, False),
        ([Interface.VIRTUAL_DEVICE], None, "ABB7F500E17A", False, False, False),
        (None, [VirtualSwitchActuator], "ABB7F500E17A", False, True, False),
        (None, [SwitchActuator], "ABB7F500E17A", False, True, True),
        (None, None, "ABB7F500E17A", True, True, False),
    ],
)
async def test_device_discovery_respects_filters(
    api_mock, interfaces, classes, source, orphan, loaded, visible
):
    """Runtime additions respect startup filters without discarding raw config."""
    api_mock.is_priming = False
    freeathome = FreeAtHome(api_mock, interfaces=interfaces, channel_classes=classes)
    await freeathome.load()
    serial = "600000000001" if source.startswith("6000") else "ABB000000001"
    device_data = deepcopy(api_mock.get_configuration.return_value["devices"][source])
    if orphan:
        for channel_data in device_data["channels"].values():
            channel_data.pop("floor")
            channel_data.pop("room")
    discovery = MagicMock()
    freeathome.register_devices_changed_callback(discovery)
    data = {"devicesAdded": [serial], "devices": {serial: device_data}}
    await freeathome.update(data)
    await freeathome.update(data)
    assert (serial in freeathome.get_devices()) is loaded
    assert bool(freeathome.get_channels_by_device(serial)) is visible
    assert serial in (await freeathome.get_config())["devices"]
    assert discovery.call_count == int(loaded)
    if classes and visible:
        assert all(
            type(channel) in classes
            for channel in freeathome.get_channels_by_device(serial)
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid",
    [
        None,
        "invalid",
        {},
        {"channels": []},
        {"channels": {"bad": []}},
        {"channels": {"bad": {"functionID": "7", "outputs": {"odp0000": []}}}},
        {"channels": {}, "parameters": ["invalid"]},
        {"channels": {"bad": {"functionID": "7", "parameters": None}}},
        {"channels": {}, "floor": 1},
        {"channels": {"bad": {"functionID": "not-hex"}}},
        {"channels": {"bad": {"inputs": []}}},
        {"channels": {"bad": {"outputs": {"odp0000": {"value": "0"}}}}},
        {
            "channels": {
                "bad": {
                    "functionID": "43",
                    "outputs": {
                        "odp0000": {
                            "pairingID": Pairing.AL_OUTDOOR_TEMPERATURE.value,
                            "value": None,
                        }
                    },
                }
            }
        },
    ],
)
async def test_invalid_addition_does_not_publish_partial_device(
    api_mock, caplog, invalid
):
    """Log rejected additions and still discover valid devices in the same frame."""
    api_mock.is_priming = False
    freeathome = FreeAtHome(api_mock)
    await freeathome.load()
    good = deepcopy(api_mock.get_configuration.return_value["devices"]["ABB7F500E17A"])
    bad_serial = "6000BAD00001"
    discovery = MagicMock()
    freeathome.register_devices_changed_callback(discovery)
    await freeathome.update(
        {
            "devicesAdded": [bad_serial, "ABB_GOOD"],
            "devices": {bad_serial: invalid, "ABB_GOOD": good},
        }
    )
    assert freeathome.get_device_by_serial(bad_serial) is None
    assert bad_serial not in (await freeathome.get_config())["devices"]
    assert freeathome.get_device_by_serial("ABB_GOOD") is not None
    discovery.assert_called_once()
    assert bad_serial in caplog.text
    assert any(record.levelname == "ERROR" for record in caplog.records)


@pytest.mark.asyncio
async def test_addition_before_initial_load(api_mock):
    """Use cached REST floorplan information even if discovery precedes load."""
    api_mock.is_priming = False
    freeathome = FreeAtHome(api_mock)
    data = deepcopy(api_mock.get_configuration.return_value["devices"]["ABB7F500E17A"])
    await freeathome.update({"devicesAdded": ["ABB_NEW"], "devices": {"ABB_NEW": data}})
    assert freeathome.get_device_by_serial("ABB_NEW").room_name == "Living Room"
    assert freeathome.get_channels()["ABB_NEW/ch0003"].state is False
    api_mock.get_configuration.assert_awaited_once()


@pytest.mark.asyncio
async def test_location_update_without_cached_config(freeathome):
    """Explicit location updates do not introduce REST requests for known objects."""
    device, channel = _params_freeathome(freeathome)
    await freeathome.update(
        {"devices": {device.device_serial: {"channels": {"ch0000": {"room": "02"}}}}}
    )
    assert device.channels["ch0000"] is channel
    assert device.channels_data["ch0000"]["room"] == "02"
    freeathome.api.get_configuration.assert_not_awaited()


@pytest.mark.asyncio
async def test_unsupported_channel_placement_does_not_notify(api_mock):
    """Keep unsupported channels filtered when their location changes."""
    api_mock.is_priming = False
    freeathome = FreeAtHome(api_mock)
    await freeathome.load()
    serial = "6000123456789"
    device = freeathome.get_device_by_serial(serial)
    discovery = MagicMock()
    freeathome.register_devices_changed_callback(discovery)
    await freeathome.update(
        {"devices": {serial: {"channels": {"ch0000": {"floor": "02", "room": "02"}}}}}
    )
    assert freeathome.get_device_by_serial(serial) is device
    assert not freeathome.get_channels_by_device(serial)
    assert (await freeathome.get_config())["devices"][serial]["channels"]["ch0000"][
        "room"
    ] == "02"
    discovery.assert_not_called()
