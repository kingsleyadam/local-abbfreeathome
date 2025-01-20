"""Free@Home Base Class for real devices."""

import logging
from typing import Any

from ..api import FreeAtHomeApi
from .base import Base

_LOGGER = logging.getLogger(__name__)


class RealBase(Base):
    """Free@Home RealBase Class."""

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
        floor_name: str | None = None,
        room_name: str | None = None,
    ) -> None:
        """Initialize the Free@Home RealBase class."""

        super().__init__(
            device_id,
            device_name,
            channel_id,
            channel_name,
            inputs,
            outputs,
            parameters,
            api,
            floor_name,
            room_name,
        )

    def update_device(self, datapoint_key: str, datapoint_value: str):
        """Update the device state."""
        _LOGGER.info(
            "%s received updated data: %s: %s",
            self.channel_name,
            datapoint_key,
            datapoint_value,
        )
        _refreshed = None
        _io_key = datapoint_key.split("/")[-1]

        if _io_key in self._outputs:
            self._outputs[_io_key]["value"] = datapoint_value
            _refreshed = self._refresh_state_from_datapoint(
                datapoint=self._outputs[_io_key]
            )

        if _refreshed and self._callbacks:
            for callback in self._callbacks:
                callback()

    async def refresh_state(self):
        """Refresh the state of the device from the api."""
        for _pairing in self._state_refresh_pairings:
            _datapoint_id, _datapoint_value = self.get_output_by_pairing(
                pairing=_pairing
            )

            _datapoint = (
                await self._api.get_datapoint(
                    device_id=self.device_id,
                    channel_id=self.channel_id,
                    datapoint=_datapoint_id,
                )
            )[0]

            self._refresh_state_from_datapoint(
                datapoint={
                    "pairingID": _pairing.value,
                    "value": _datapoint,
                }
            )

    def _refresh_state_from_datapoints(self):
        """Refresh the state of the device from the datapoints."""
        for _datapoint in self._outputs.values():
            self._refresh_state_from_datapoint(_datapoint)
