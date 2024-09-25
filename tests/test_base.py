"""Test class to test the Base device."""

from unittest.mock import MagicMock

import pytest

from abbfreeathome.api import FreeAtHomeApi
from abbfreeathome.devices.base import Base
from abbfreeathome.exceptions import InvalidDeviceChannelPairingId


class TestBase:
    """The TestBase class for testing the Base device."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up the test class."""
        self.api = MagicMock(spec=FreeAtHomeApi)
        self.device_id = "device123"
        self.device_name = "Device Name"
        self.channel_id = "channel123"
        self.channel_name = "Channel Name"
        self.inputs = {
            "input1": {"pairingID": 1, "value": "input_value1"},
            "input2": {"pairingID": 2, "value": "input_value2"},
        }
        self.outputs = {
            "output1": {"pairingID": 1, "value": "output_value1"},
            "output2": {"pairingID": 2, "value": "output_value2"},
        }
        self.parameters = {}
        self.base = Base(
            self.device_id,
            self.device_name,
            self.channel_id,
            self.channel_name,
            self.inputs,
            self.outputs,
            self.parameters,
            self.api,
        )

    def test_device_id(self):
        """Test the device id."""
        assert self.base.device_id == self.device_id

    def test_device_name(self):
        """Test the device name."""
        assert self.base.device_name == self.device_name

    def test_channel_id(self):
        """Test the channel id."""
        assert self.base.channel_id == self.channel_id

    def test_channel_name(self):
        """Test the channel name."""
        assert self.base.channel_name == self.channel_name

    def test_get_input_by_pairing_id(self):
        """Test the get_input_by_paring_id function."""
        input_id, value = self.base.get_input_by_pairing_id(1)
        assert input_id == "input1"
        assert value == "input_value1"

        with pytest.raises(InvalidDeviceChannelPairingId):
            self.base.get_input_by_pairing_id(99)

    def test_get_output_by_pairing_id(self):
        """Test the get_output_by_pairing_id function."""
        output_id, value = self.base.get_output_by_pairing_id(1)
        assert output_id == "output1"
        assert value == "output_value1"

        with pytest.raises(InvalidDeviceChannelPairingId):
            self.base.get_output_by_pairing_id(99)

    def test_register_callback(self):
        """Test register a callback."""
        callback = MagicMock()
        self.base.register_callback(callback)
        assert callback in self.base._callbacks  # noqa: SLF001

    def test_remove_callback(self):
        """Test removing a callback."""
        callback = MagicMock()
        self.base.register_callback(callback)
        self.base.remove_callback(callback)
        assert callback not in self.base._callbacks  # noqa: SLF001
