"""Test virtual dimming requests, mapping and WebSocket dispatch."""

from unittest.mock import AsyncMock, Mock, call

import pytest

from src.abbfreeathome.api import FreeAtHomeApi
from src.abbfreeathome.bin.function import Function
from src.abbfreeathome.bin.interface import Interface
from src.abbfreeathome.bin.pairing import Pairing
from src.abbfreeathome.channels.dimming_actuator import DimmingActuator
from src.abbfreeathome.channels.switch_sensor import DimmingSensor
from src.abbfreeathome.channels.virtual.virtual_dimming_actuator import (
    VirtualDimmingActuator,
)
from src.abbfreeathome.channels.virtual.virtual_switch_actuator import (
    VirtualSwitchActuator,
)
from src.abbfreeathome.device import Device
from src.abbfreeathome.freeathome import FreeAtHome


@pytest.fixture
def device(mock_floorplan):
    """Build a virtual channel with the observed input IDs and ABB pairings."""
    instance = Device(
        device_serial="6000F66D1DA7",
        device_id="test",
        display_name="Virtual Dimmer",
        api=AsyncMock(spec=FreeAtHomeApi),
        interface=Interface.VIRTUAL_DEVICE,
        channels_data={
            "ch0000": {
                "functionID": "0012",
                "inputs": {
                    "idp0000": {"pairingID": 1, "value": "1"},
                    "idp0001": {"pairingID": 16, "value": "9"},
                    "idp0002": {"pairingID": 17, "value": "50"},
                },
                "outputs": {"odp0000": {"pairingID": 256, "value": "0"}},
            },
        },
    )
    # Test live requests after the reconnect snapshot has finished.
    instance.api.is_priming = False
    instance.load_channels(mock_floorplan)
    return instance


@pytest.fixture
def dimmer(device):
    """Return the channel created through the virtual function mapping."""
    return device.channels["ch0000"]


def test_initialization(dimmer):
    """Initialize requests from inputs without overwriting actual feedback."""
    assert type(dimmer) is VirtualDimmingActuator
    assert dimmer.is_virtual is True
    assert dimmer.state is False
    assert dimmer.requested_state is True
    assert dimmer.requested_dimming_state == "longpress_up"


def test_empty_initialization(device):
    """Keep missing requests unknown until data arrives."""
    channel = VirtualDimmingActuator(device, "ch0000", "Dimmer", {}, {}, {})
    assert channel.state is None
    assert channel.requested_state is None
    assert channel.requested_dimming_state == "unknown"


@pytest.mark.parametrize(
    ("interface", "function", "expected"),
    [
        (
            Interface.VIRTUAL_DEVICE,
            Function.FID_DIMMING_ACTUATOR,
            VirtualDimmingActuator,
        ),
        (Interface.WIRED_BUS, Function.FID_DIMMING_ACTUATOR, DimmingActuator),
        (Interface.WIRED_BUS, Function.FID_DIMMING_ACTUATOR_TYPE0, DimmingActuator),
        (Interface.WIRED_BUS, Function.FID_DIMMING_SENSOR, DimmingSensor),
        (Interface.VIRTUAL_DEVICE, Function.FID_SWITCH_ACTUATOR, VirtualSwitchActuator),
    ],
)
def test_channel_mapping(interface, function, expected, mock_floorplan):
    """Select the virtual dimmer without changing existing channel mappings."""
    instance = Device(
        "test",
        "test",
        "Test",
        AsyncMock(spec=FreeAtHomeApi),
        interface=interface,
        channels_data={"ch0000": {"functionID": f"{function.value:04X}"}},
    )
    assert type(instance.load_channels(mock_floorplan)["ch0000"]) is expected


@pytest.mark.parametrize(("value", "expected"), [("1", True), ("0", False)])
def test_switch_request(dimmer, value, expected):
    """Process idp0000 without interpreting it as dimming or actual state."""
    callback = Mock()
    unrelated = Mock()
    dimmer.register_callback("requested_state", callback)
    dimmer.register_callback("requested_dimming_state", unrelated)
    dimmer.register_callback("state", unrelated)
    dimmer.update_channel("6000F66D1DA7/ch0000/idp0000", value)
    assert dimmer.requested_state is expected
    assert dimmer.state is False
    assert dimmer.requested_dimming_state == "longpress_up"
    callback.assert_called_once_with()
    unrelated.assert_not_called()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("9", "longpress_up"),
        ("8", "longpress_up_release"),
        ("1", "longpress_down"),
        ("0", "longpress_down_release"),
        ("7", "unknown"),
        ("invalid", "unknown"),
    ],
)
def test_dimming_request(dimmer, value, expected):
    """Reuse sensor command semantics and notify for every telegram."""
    callback = Mock()
    unrelated = Mock()
    dimmer.register_callback("requested_dimming_state", callback)
    dimmer.register_callback("requested_state", unrelated)
    dimmer.register_callback("state", unrelated)
    for _ in range(2):
        dimmer.update_channel("6000F66D1DA7/ch0000/idp0001", value)
    assert dimmer.requested_dimming_state == expected
    assert dimmer.requested_state is True
    assert dimmer.state is False
    assert callback.call_args_list == [call(), call()]
    unrelated.assert_not_called()
    dimmer.remove_callback("requested_dimming_state", callback)
    dimmer.update_channel("6000F66D1DA7/ch0000/idp0001", value)
    assert callback.call_count == 2


def test_updates_without_callbacks(dimmer):
    """Accept input and output updates even before callbacks are registered."""
    dimmer.update_channel("idp0000", "0")
    dimmer.update_channel("idp0001", "8")
    dimmer.update_channel("odp0000", "1")
    assert dimmer.requested_state is False
    assert dimmer.requested_dimming_state == "longpress_up_release"
    assert dimmer.state is True
    assert dimmer.get_input_by_pairing(Pairing.AL_RELATIVE_SET_VALUE_CONTROL) == (
        "idp0001",
        "8",
    )


def test_pairing_based_dispatch(dimmer):
    """Identify commands by pairing, not by a hardcoded input number."""
    dimmer._inputs["idp0015"] = dimmer._inputs.pop("idp0001")
    dimmer.update_channel("idp0015", "1")
    assert dimmer.requested_dimming_state == "longpress_down"
    dimmer.update_channel("idp0001", "9")
    dimmer.update_channel("idp0002", "80")
    assert dimmer.requested_dimming_state == "longpress_down"


def test_feedback_callback(dimmer):
    """Keep actual feedback distinct from the requested switch state."""
    callback = Mock()
    dimmer.register_callback("state", callback)
    dimmer.update_channel("odp0000", "1")
    callback.assert_called_once_with()
    assert dimmer.state is True
    assert dimmer.requested_dimming_state == "longpress_up"


@pytest.mark.asyncio
async def test_refresh_state(dimmer, device):
    """Refresh feedback and both supported input pairings."""
    device.api.get_datapoint.side_effect = [["1"], ["0"], ["8"]]
    await dimmer.refresh_state()
    assert dimmer.state is True
    assert dimmer.requested_state is False
    assert dimmer.requested_dimming_state == "longpress_up_release"
    assert device.api.get_datapoint.await_args_list == [
        call(device_serial="6000F66D1DA7", channel_id="ch0000", datapoint=datapoint)
        for datapoint in ("odp0000", "idp0000", "idp0001")
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(("method", "value"), [("turn_on", "1"), ("turn_off", "0")])
async def test_switch_feedback(dimmer, device, method, value):
    """Publish switch feedback to the output, as for a virtual switch."""
    await getattr(dimmer, method)()
    device.api.set_datapoint.assert_awaited_once_with(
        device_serial="6000F66D1DA7",
        channel_id="ch0000",
        datapoint="odp0000",
        value=value,
    )
    assert dimmer.state is (value == "1")
    assert dimmer.requested_state is True


@pytest.mark.asyncio
async def test_websocket_dispatch(device, dimmer):
    """Route observed telegrams through the actual WebSocket callback."""
    freeathome = FreeAtHome(device.api, include_orphan_channels=True)
    freeathome._devices[device.device_serial] = device
    observed = []
    dimmer.register_callback(
        "requested_dimming_state",
        lambda: observed.append(dimmer.requested_dimming_state),
    )
    for value in ("9", "8", "1", "0"):
        await freeathome.update({"datapoints": {"6000F66D1DA7/ch0000/idp0001": value}})
    assert observed == [
        "longpress_up",
        "longpress_up_release",
        "longpress_down",
        "longpress_down_release",
    ]
    for value in ("1", "0"):
        await freeathome.update({"datapoints": {"6000F66D1DA7/ch0000/idp0000": value}})
        assert dimmer.requested_state is (value == "1")


@pytest.mark.asyncio
async def test_snapshot_replay_suppresses_unchanged_dimmer(device, dimmer):
    """Suppress replayed requests while allowing identical live dimmer presses."""
    freeathome = FreeAtHome(device.api, include_orphan_channels=True)
    freeathome._devices[device.device_serial] = device
    requested = Mock()
    dimmer.register_callback("requested_dimming_state", requested)
    device.api.is_priming = True
    await freeathome.update({"datapoints": {"6000F66D1DA7/ch0000/idp0001": "9"}})
    requested.assert_not_called()
    device.api.is_priming = False
    await freeathome.update({"datapoints": {"6000F66D1DA7/ch0000/idp0001": "9"}})
    requested.assert_called_once()
