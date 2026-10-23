"""Free@Home Virtual Trigger class."""

import logging
from typing import TYPE_CHECKING, Any

from ...bin.pairing import Pairing
from ..trigger import Trigger

if TYPE_CHECKING:
    from ...device import Device

_LOGGER = logging.getLogger(__name__)


class VirtualTrigger(Trigger):
    """Free@Home Virtual Trigger Class."""

    _input_refresh_pairings: list[Pairing] = [
        Pairing.AL_TIMED_START_STOP,
    ]
    _callback_attributes: list[str] = [
        "triggered",
    ]

    def __init__(
        self,
        device: "Device",
        channel_id: str,
        channel_name: str,
        inputs: dict[str, dict[str, Any]],
        outputs: dict[str, dict[str, Any]],
        parameters: dict[str, dict[str, Any]],
        floor_name: str | None = None,
        room_name: str | None = None,
    ) -> None:
        """Initialize the Free@Home Virtual Trigger class."""
        self._triggered: bool | None = None

        super().__init__(
            device,
            channel_id,
            channel_name,
            inputs,
            outputs,
            parameters,
            floor_name,
            room_name,
        )

    @property
    def triggered(self) -> bool | None:
        """Get the triggered state."""
        return self._triggered

    def _refresh_state_from_datapoint(self, datapoint: dict[str, Any]) -> list[str]:
        """
        Refresh the state of the channel from a given output.

        Return the names of the attributes refreshed by this datapoint.
        """
        if datapoint.get("pairingID") == Pairing.AL_TIMED_START_STOP.value:
            self._triggered = datapoint.get("value") == "1"
            return ["triggered"]
        return []

    def update_channel(
        self, datapoint_key: str, datapoint_value: str, is_priming: bool = False
    ):
        """Update the device state."""
        _LOGGER.info(
            "%s received updated data: %s: %s",
            self.channel_name,
            datapoint_key,
            datapoint_value,
        )
        _callback_attributes: list[str] = []
        _changed = True
        _io_key = datapoint_key.rsplit("/", maxsplit=1)[-1]

        if _io_key in self._outputs:
            _changed = self._outputs[_io_key].get("value") != datapoint_value
            self._outputs[_io_key]["value"] = datapoint_value
            _callback_attributes = self._refresh_state_from_datapoint(
                datapoint=self._outputs[_io_key]
            )

        if _io_key in self._inputs:
            _changed = self._inputs[_io_key].get("value") != datapoint_value
            self._inputs[_io_key]["value"] = datapoint_value
            _callback_attributes = self._refresh_state_from_datapoint(
                datapoint=self._inputs[_io_key]
            )

        if is_priming and not _changed:
            return

        self._notify_callbacks(_callback_attributes)
