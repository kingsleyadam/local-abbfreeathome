"""Free@Home Base Class."""

from typing import Any

from ..api import FreeAtHomeApi


class Base:
    """Free@Home Base Class."""

    def __init__(
        self,
        device_id: str,
        device_name: str,
        channel_id: str,
        channel_name: str,
        inputs: dict[str, dict[str, Any]],
        outputs: dict[str, dict[str, Any]],
        parameters: dict[str, dict[str, Any]],
        api: FreeAtHomeApi,
    ) -> None:
        """Initialize the Free@Home Base class."""
        self._device_id = device_id
        self._device_name = device_name
        self._channel_id = channel_id
        self._channel_name = channel_name
        self._api = api
        self._inputs = inputs
        self._outputs = outputs
        self._parameters = parameters

    @property
    def device_id(self) -> str:
        """Get the device id."""
        return self._device_id

    @property
    def device_name(self) -> str:
        """Get the device name."""
        return self._device_name

    @property
    def channel_id(self) -> str:
        """Get the channel id."""
        return self._channel_id

    @property
    def channel_name(self) -> str:
        """Get the name of the channel."""
        return self._channel_name

    def get_input_by_pairing_id(self, pairing_id: int) -> tuple[str, Any]:
        """Get the channel input by pairing id."""
        for _input_id, _input in self._inputs.items():
            if _input.get("pairingID") == pairing_id:
                return _input_id, _input.get("value")

        raise ValueError(
            f"Could not find input for device: {self.device_id}; channel: {self.channel_id}; pairing id: {pairing_id}"
        )

    def get_output_by_pairing_id(self, pairing_id: int) -> tuple[str, Any]:
        """Get the channel output by pairing id."""
        for _output_id, _output in self._outputs.items():
            if _output.get("pairingID") == pairing_id:
                return _output_id, _output.get("value")

        raise ValueError(
            f"Could not find output for device: {self.device_id}; channel: {self.channel_id}; pairing id: {pairing_id}"
        )
