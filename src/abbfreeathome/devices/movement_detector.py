"""Free@Home MovementDetectorSensor Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing import Pairing
from .base import Base


class MovementDetector(Base):
    """Free@Home SwitchActuator Class."""

    _state = None

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
        """Initialize the Free@Home SwitchActuator class."""
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

        # Set the initial state of the switch based on output
        self._refresh_state_from_outputs()

    @property
    def brightness(self):
        """Get the brightness level of the sensor."""
        return self._brightness

    async def refresh_state(self):
        """Refresh the state of the device from the api."""
        _switch_output_id, _switch_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_BRIGHTNESS_LEVEL
        )

        _datapoint = (
            await self._api.get_datapoint(
                device_id=self.device_id,
                channel_id=self.channel_id,
                datapoint=_switch_output_id,
            )
        )[0]

        self._brightness = _datapoint

    def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
        """
        Refresh the state of the device from a given output.

        This will return whether the state was refreshed as a boolean value.
        """
        if output.get("pairingID") == Pairing.AL_BRIGHTNESS_LEVEL.value:
            self._brightness = output.get("value")
            return True
        return False

    def _refresh_state_from_outputs(self):
        """Refresh the state of the switch from the _outputs."""
        _switch_output_id, _switch_output_value = self.get_output_by_pairing(
            pairing=Pairing.AL_BRIGHTNESS_LEVEL
        )
        self._brightness = _switch_output_value
