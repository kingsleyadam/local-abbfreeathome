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
from src.abbfreeathome.exceptions import (
    InvalidApiResponseException,
    InvalidDeviceChannelPairing,
)
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
                "outputs": {
                    "odp0000": {"pairingID": 256, "value": "0"},
                    "odp0001": {"pairingID": 272, "value": "20"},
                },
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
    assert dimmer.requested_brightness == 50
    assert dimmer.brightness == 20


def test_empty_initialization(device):
    """Keep missing requests unknown until data arrives."""
    channel = VirtualDimmingActuator(device, "ch0000", "Dimmer", {}, {}, {})
    assert channel.state is None
    assert channel.requested_state is None
    assert channel.requested_dimming_state == "unknown"
    assert channel.requested_brightness is None
    assert channel.brightness is None


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


@pytest.mark.parametrize("value", [None, "", "invalid", "2", "01", " 1", 0, 1, True])
def test_invalid_switch_request(dimmer, value):
    """Surface invalid switching inputs as unknown without changing feedback."""
    requested_states = []
    unrelated = Mock()
    dimmer.register_callback(
        "requested_state", lambda: requested_states.append(dimmer.requested_state)
    )
    dimmer.register_callback("state", unrelated)

    for request_value in (value, "0", "1"):
        dimmer.update_channel("6000F66D1DA7/ch0000/idp0000", request_value)

    assert requested_states == [None, False, True]
    assert dimmer.state is False
    unrelated.assert_not_called()


@pytest.mark.parametrize("value", [None, "", "invalid", "2"])
def test_invalid_initial_switch_request(device, value):
    """Do not initialize malformed switching inputs as off requests."""
    channel = VirtualDimmingActuator(
        device,
        "ch0000",
        "Dimmer",
        {"idp0000": {"pairingID": 1, "value": value}},
        {},
        {},
    )
    assert channel.requested_state is None


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
    dimmer.update_channel("idp0002", "42.5")
    dimmer.update_channel("odp0000", "1")
    assert dimmer.requested_state is False
    assert dimmer.requested_dimming_state == "longpress_up_release"
    assert dimmer.state is True
    assert dimmer.requested_brightness == 42.5
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
    dimmer._inputs["idp0016"] = dimmer._inputs.pop("idp0002")
    dimmer.update_channel("idp0016", "80")
    assert dimmer.requested_dimming_state == "longpress_down"
    assert dimmer.requested_brightness == 80
    dimmer.update_channel("idp0002", "20")
    assert dimmer.requested_brightness == 80


@pytest.mark.parametrize(
    ("value", "expected"),
    [("0", 0), ("100", 100), ("40", 40), ("40.5", 40.5), ("50.0", 50)],
)
def test_brightness_requests(dimmer, device, value, expected):
    """Preserve percentages and repeated live requests without changing feedback."""
    requested = Mock()
    unrelated = Mock()
    dimmer.register_callback("requested_brightness", requested)
    for attribute in (
        "state",
        "brightness",
        "requested_state",
        "requested_dimming_state",
    ):
        dimmer.register_callback(attribute, unrelated)
    for _ in range(2):
        dimmer.update_channel("idp0002", value)
    assert dimmer.requested_brightness == expected
    assert requested.call_args_list == [call(), call()]
    assert dimmer.state is False
    assert dimmer.requested_state is True
    assert dimmer.requested_dimming_state == "longpress_up"
    assert dimmer.brightness == 20
    unrelated.assert_not_called()
    device.api.set_datapoint.assert_not_called()
    dimmer.remove_callback("requested_brightness", requested)
    dimmer.update_channel("idp0002", value)
    assert requested.call_count == 2


@pytest.mark.parametrize(
    "value", ["invalid", "-1", "100.1", "nan", "inf", "-inf", True, [], {}]
)
def test_invalid_brightness_ignored(dimmer, caplog, value):
    """Reject invalid requests visibly without emitting the previous valid value."""
    requested = Mock()
    dimmer.register_callback("requested_brightness", requested)
    dimmer.update_channel("idp0002", value)
    assert dimmer.requested_brightness == 50
    requested.assert_not_called()
    assert "brightness" in caplog.text


@pytest.mark.parametrize("value", [None, ""])
def test_unset_brightness(device, value):
    """Treat unpopulated configuration inputs as unknown, not zero."""
    channel = VirtualDimmingActuator(
        device,
        "ch0000",
        "Dimmer",
        {"idp0002": {"pairingID": 17, "value": value}},
        {},
        {},
    )
    assert channel.requested_brightness is None


def test_brightness_feedback_is_not_a_request(dimmer):
    """Actual brightness outputs must not emit an absolute-brightness request."""
    requested = Mock()
    dimmer.register_callback("requested_brightness", requested)
    dimmer._outputs["odp0001"] = {"pairingID": 272, "value": "0"}
    dimmer.update_channel("odp0001", "80")
    assert dimmer.requested_brightness == 50
    assert dimmer.brightness == 80
    requested.assert_not_called()


@pytest.mark.parametrize(
    ("value", "expected"), [("0", 0), ("100", 100), ("42.5", 42), ("50.0", 50)]
)
def test_reported_brightness(dimmer, device, value, expected):
    """Decode actual brightness without changing On/Off or requested values."""
    feedback = Mock()
    unrelated = Mock()
    dimmer.register_callback("brightness", feedback)
    for attribute in (
        "state",
        "requested_state",
        "requested_dimming_state",
        "requested_brightness",
    ):
        dimmer.register_callback(attribute, unrelated)
    dimmer.update_channel("odp0001", value)
    assert dimmer.brightness == expected
    assert dimmer.state is False
    assert dimmer.requested_state is True
    assert dimmer.requested_brightness == 50
    feedback.assert_called_once_with()
    unrelated.assert_not_called()
    device.api.set_datapoint.assert_not_called()
    dimmer.remove_callback("brightness", feedback)
    dimmer.update_channel("odp0001", value)
    assert feedback.call_count == 1


@pytest.mark.parametrize(
    "value", ["invalid", "-1", "100.1", "nan", "inf", "-inf", True, [], {}]
)
def test_invalid_reported_brightness(dimmer, caplog, value):
    """Do not replace good feedback or notify consumers with invalid values."""
    feedback = Mock()
    dimmer.register_callback("brightness", feedback)
    dimmer.update_channel("odp0001", value)
    assert dimmer.brightness == 20
    feedback.assert_not_called()
    assert "brightness feedback" in caplog.text


@pytest.mark.parametrize("value", [None, ""])
def test_unknown_reported_brightness(device, value):
    """An empty configuration value is unknown, rather than invented zero."""
    channel = VirtualDimmingActuator(
        device,
        "ch0000",
        "Dimmer",
        {},
        {"odp0001": {"pairingID": 272, "value": value}},
        {},
    )
    assert channel.brightness is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("value", "expected"), [(-1, 1), (0, 1), (1, 1), (40, 40), (100, 100), (101, 100)]
)
async def test_set_brightness_feedback(dimmer, device, value, expected):
    """Publish only the brightness output using physical-dimmer clamping."""
    callback = Mock()
    for attribute in dimmer._callback_attributes:
        dimmer.register_callback(attribute, callback)
    await dimmer.set_brightness(value)
    assert dimmer.brightness == expected
    assert dimmer.state is False
    assert dimmer.requested_brightness == 50
    device.api.set_datapoint.assert_awaited_once_with(
        device_serial="6000F66D1DA7",
        channel_id="ch0000",
        datapoint="odp0001",
        value=str(expected),
    )
    callback.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value", [True, False, 40.5, "50", None, float("nan"), float("inf")]
)
async def test_invalid_brightness_setter(dimmer, device, value):
    """Reject non-integer arguments before writing or changing local feedback."""
    with pytest.raises(TypeError, match="integer percentage"):
        await dimmer.set_brightness(value)
    assert dimmer.brightness == 20
    device.api.set_datapoint.assert_not_called()


@pytest.mark.asyncio
async def test_failed_brightness_write(dimmer, device):
    """A synchronous API failure must not change the local property."""
    device.api.set_datapoint.side_effect = InvalidApiResponseException(503)
    with pytest.raises(InvalidApiResponseException, match="503"):
        await dimmer.set_brightness(70)
    assert dimmer.brightness == 20


@pytest.mark.asyncio
async def test_brightness_output_pairing(dimmer, device):
    """Read and write by pairing instead of assuming the observed output ID."""
    dimmer._outputs["odp0015"] = dimmer._outputs.pop("odp0001")
    dimmer.update_channel("odp0015", "65")
    assert dimmer.brightness == 65
    dimmer.update_channel("odp0001", "80")
    assert dimmer.brightness == 65
    await dimmer.set_brightness(70)
    device.api.set_datapoint.assert_awaited_once_with(
        device_serial="6000F66D1DA7",
        channel_id="ch0000",
        datapoint="odp0015",
        value="70",
    )


@pytest.mark.asyncio
async def test_missing_brightness_output(dimmer, device):
    """A missing feedback pairing raises the existing capability exception."""
    del dimmer._outputs["odp0001"]
    with pytest.raises(InvalidDeviceChannelPairing, match="272"):
        await dimmer.set_brightness(70)
    assert dimmer.brightness == 20
    device.api.set_datapoint.assert_not_called()


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
    """Refresh feedback and all supported input pairings without callbacks."""
    requested = Mock()
    dimmer.register_callback("requested_brightness", requested)
    feedback = Mock()
    dimmer.register_callback("brightness", feedback)
    device.api.get_datapoint.side_effect = [["1"], ["42.5"], ["0"], ["8"], ["65.5"]]
    await dimmer.refresh_state()
    assert dimmer.state is True
    assert dimmer.requested_state is False
    assert dimmer.requested_dimming_state == "longpress_up_release"
    assert dimmer.requested_brightness == 65.5
    assert dimmer.brightness == 42
    requested.assert_not_called()
    feedback.assert_not_called()
    assert device.api.get_datapoint.await_args_list == [
        call(device_serial="6000F66D1DA7", channel_id="ch0000", datapoint=datapoint)
        for datapoint in ("odp0000", "odp0001", "idp0000", "idp0001", "idp0002")
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("pairing", [2, 3, 4, 6, 18, 999])
async def test_unsupported_inputs_are_not_refreshed(device, pairing):
    """Ignore unused and unknown inputs during initialization and API refresh."""
    data = device.channels_data["ch0000"]
    inputs = {key: dict(point) for key, point in data["inputs"].items()} | {
        "idp00ff": {"pairingID": pairing, "value": "unsupported"}
    }
    channel = VirtualDimmingActuator(
        device,
        "ch0000",
        "Dimmer",
        inputs,
        {key: dict(point) for key, point in data["outputs"].items()},
        {},
    )
    assert channel.state is False
    assert channel.brightness == 20
    assert channel.requested_state is True
    assert channel.requested_dimming_state == "longpress_up"
    assert channel.requested_brightness == 50
    device.api.get_datapoint.assert_not_called()

    callback = Mock()
    for attribute in channel._callback_attributes:
        channel.register_callback(attribute, callback)
    device.api.get_datapoint.side_effect = [["1"], ["42"], ["0"], ["8"], ["65.5"]]
    await channel.refresh_state()

    assert channel.state is True
    assert channel.brightness == 42
    assert channel.requested_state is False
    assert channel.requested_dimming_state == "longpress_up_release"
    assert channel.requested_brightness == 65.5
    assert inputs["idp00ff"]["value"] == "unsupported"
    assert device.api.get_datapoint.await_args_list == [
        call(device_serial="6000F66D1DA7", channel_id="ch0000", datapoint=datapoint)
        for datapoint in ("odp0000", "odp0001", "idp0000", "idp0001", "idp0002")
    ]
    callback.assert_not_called()
    device.api.set_datapoint.assert_not_called()


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


@pytest.mark.asyncio
async def test_brightness_websocket_and_priming(device, dimmer):
    """Suppress unchanged snapshots but preserve live repeats and changed snapshots."""
    freeathome = FreeAtHome(device.api, include_orphan_channels=True)
    freeathome._devices[device.device_serial] = device
    observed = []
    dimmer.register_callback(
        "requested_brightness", lambda: observed.append(dimmer.requested_brightness)
    )
    device.api.is_priming = True
    await freeathome.update({"datapoints": {"6000F66D1DA7/ch0000/idp0002": "50"}})
    assert observed == []
    await freeathome.update({"datapoints": {"6000F66D1DA7/ch0000/idp0002": "60.5"}})
    assert observed == [60.5]
    device.api.is_priming = False
    for _ in range(2):
        await freeathome.update({"datapoints": {"6000F66D1DA7/ch0000/idp0002": "60.5"}})
    assert observed == [60.5, 60.5, 60.5]
    device.api.is_priming = True
    await freeathome.update({"datapoints": {"6000F66D1DA7/ch0000/idp0002": "60.5"}})
    assert observed == [60.5, 60.5, 60.5]


@pytest.mark.asyncio
async def test_feedback_websocket_and_priming(device, dimmer):
    """Suppress unchanged output snapshots without emitting any request callback."""
    freeathome = FreeAtHome(device.api, include_orphan_channels=True)
    freeathome._devices[device.device_serial] = device
    observed = []
    requested = Mock()
    dimmer.register_callback("brightness", lambda: observed.append(dimmer.brightness))
    dimmer.register_callback("requested_brightness", requested)
    device.api.is_priming = True
    await freeathome.update({"datapoints": {"6000F66D1DA7/ch0000/odp0001": "20"}})
    assert observed == []
    await freeathome.update({"datapoints": {"6000F66D1DA7/ch0000/odp0001": "70"}})
    assert observed == [70]
    device.api.is_priming = False
    await freeathome.update({"datapoints": {"6000F66D1DA7/ch0000/odp0001": "70"}})
    assert observed == [70, 70]
    requested.assert_not_called()
    device.api.is_priming = True
    await freeathome.update({"datapoints": {"6000F66D1DA7/ch0000/odp0001": "70"}})
    assert observed == [70, 70]
