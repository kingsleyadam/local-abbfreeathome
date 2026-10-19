"""Test scene notifications using the observed SysAP WebSocket format."""

from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.channels.scene import Scene
from src.abbfreeathome.freeathome import FreeAtHome

SERIAL = "FFFF4800000A"
DATAPOINT = f"{SERIAL}/ch0000/odp0000"


@pytest.fixture
def api():
    """Return a scene configuration with a cached, non-empty output value."""
    api = AsyncMock(spec=FreeAtHomeApi)
    # Test live requests after the reconnect snapshot has finished.
    api.is_priming = False
    api.get_configuration.return_value = {
        "devices": {
            SERIAL: {
                "displayName": "Upstairs night lights",
                "interface": "scene",
                "channels": {
                    "ch0000": {
                        "displayName": "Upstairs night lights",
                        "functionID": "4800",
                        "floor": "02",
                        "room": "0A",
                        "inputs": {"idp0000": {"pairingID": 4, "value": "2"}},
                        "outputs": {
                            "odp0000": {"pairingID": 4, "value": "2"},
                            "odp0001": {"pairingID": 256, "value": "0"},
                        },
                    }
                },
            }
        },
        "floorplan": {"floors": {}},
    }
    return api


@pytest_asyncio.fixture
async def freeathome(api):
    """Load the real channel through the normal function mapping."""
    instance = FreeAtHome(api)
    await instance.load()
    return instance


@pytest.mark.asyncio
@pytest.mark.parametrize("function_id", ["4800", "4801", "4802"])
async def test_scene_function_mapping(api, function_id):
    """Load regular, panic and all-off scenes through their function IDs."""
    channel = api.get_configuration.return_value["devices"][SERIAL]["channels"]
    channel["ch0000"]["functionID"] = function_id
    freeathome = FreeAtHome(api)
    await freeathome.load()
    scenes = freeathome.get_channels_by_class(Scene)
    assert len(scenes) == 1
    assert scenes[0].device_serial == SERIAL
    assert scenes[0].channel_name == "Upstairs night lights"


@pytest.mark.asyncio
async def test_repeated_scene_requests(freeathome):
    """Deliver all three identical telegrams instead of comparing state values."""
    scene = freeathome.get_channels_by_class(Scene)[0]
    requested = Mock()
    scene.register_callback("scene_control", requested)

    for _ in range(3):
        await freeathome.update({"datapoints": {DATAPOINT: "2"}, "scenesTriggered": {}})

    assert requested.call_count == 3
    assert scene.scene_control == "2"


@pytest.mark.asyncio
async def test_cached_value_and_refresh_do_not_emit_requests(freeathome, api):
    """Loading or refreshing state must not replay a previous scene request."""
    scene = freeathome.get_channels_by_class(Scene)[0]
    requested = Mock()
    scene.register_callback("scene_control", requested)
    assert scene.scene_control == "2"
    requested.assert_not_called()

    scene._refresh_state_from_datapoints()
    await scene.refresh_state()
    requested.assert_not_called()
    api.get_datapoint.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [None, "", "invalid", "128", "255", "-1", "256", 2])
async def test_invalid_and_learning_values_do_not_emit(freeathome, value):
    """Ignore malformed payloads and the DPT scene-control learning bit."""
    scene = freeathome.get_channels_by_class(Scene)[0]
    requested = Mock()
    scene.register_callback("scene_control", requested)
    await freeathome.update({"datapoints": {DATAPOINT: value}})
    requested.assert_not_called()


@pytest.mark.asyncio
async def test_unrelated_and_input_datapoints_do_not_emit(freeathome):
    """Only the scene-control output represents this scene's notification."""
    scene = freeathome.get_channels_by_class(Scene)[0]
    requested = Mock()
    scene.register_callback("scene_control", requested)
    await freeathome.update(
        {
            "datapoints": {
                f"{SERIAL}/ch0000/idp0000": "2",
                f"{SERIAL}/ch0000/odp0001": "1",
                f"{SERIAL}/ch0000/odp9999": "2",
                "UNKNOWN/ch0000/odp0000": "2",
            }
        }
    )
    requested.assert_not_called()


@pytest.mark.asyncio
async def test_updates_without_subscribers_and_after_removal(freeathome):
    """Handle notifications safely before subscription and after removal."""
    scene = freeathome.get_channels_by_class(Scene)[0]
    scene.update_channel(DATAPOINT, "2")
    requested = Mock()
    scene.register_callback("scene_control", requested)
    scene.remove_callback("scene_control", requested)
    scene.update_channel(DATAPOINT, "2")
    requested.assert_not_called()


@pytest.mark.asyncio
async def test_mixed_websocket_message(freeathome):
    """Ignore other devices while preserving the scene notification."""
    scene = freeathome.get_channels_by_class(Scene)[0]
    requested = Mock()
    scene.register_callback("scene_control", requested)
    await freeathome.update(
        {
            "datapoints": {
                "BEED00000001/ch0000/odp0000": "1",
                DATAPOINT: "2",
                "BEED00000001/ch0000/odp0001": "100",
            },
            "scenesTriggered": {},
        }
    )
    requested.assert_called_once()


@pytest.mark.asyncio
async def test_snapshot_replay_suppresses_unchanged_scene(freeathome, api):
    """Suppress cached snapshot values while preserving identical live requests."""
    scene = freeathome.get_channels_by_class(Scene)[0]
    requested = Mock()
    scene.register_callback("scene_control", requested)
    api.is_priming = True
    await freeathome.update({"datapoints": {DATAPOINT: "2"}})
    requested.assert_not_called()
    api.is_priming = False
    await freeathome.update({"datapoints": {DATAPOINT: "2"}})
    requested.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_priming", [False, True])
async def test_explicit_scene_requests_during_priming(freeathome, api, is_priming):
    """Emit repeated scene notifications once even if also listed as datapoints."""
    scene = freeathome.get_channels_by_class(Scene)[0]
    requested = Mock()
    scene.register_callback("scene_control", requested)
    api.is_priming = is_priming
    for _ in range(3):
        await freeathome.update(
            {
                "datapoints": {DATAPOINT: "2"},
                "scenesTriggered": {
                    SERIAL: {
                        "channels": {
                            "ch0000": {
                                "outputs": {"odp0000": {"pairingID": 4, "value": "2"}}
                            }
                        }
                    }
                },
            }
        )
    assert requested.call_count == 3
