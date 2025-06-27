"""Free@Home Trigger Class."""

import logging
from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base

_LOGGER = logging.getLogger(__name__)


class Trigger(Base):
    """Free@Home Trigger Class."""

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
        """Initialize the Free@Home Trigger class."""
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

    async def press(self):
        """Press the trigger."""
        await self._set_trigger_datapoint()

    async def _set_trigger_datapoint(self):
        _trigger_input_id, _trigger_input_value = self.get_input_by_pairing(
            pairing=Pairing.AL_TIMED_START_STOP
        )
        return await self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_trigger_input_id,
            value="1",
        )
