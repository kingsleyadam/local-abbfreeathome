"""Free@Home Switch Class."""

from typing import Any

from ..api import FreeAtHomeApi
from ..bin.pairing_id import PairingId
from .base import Base


class Switch(Base):
    """Free@Home Switch Class."""

    _state = None

    def __init__(
        self,
        device_id: str,
        channel_id: str,
        name: str,
        inputs: dict[str, dict[str, Any]],
        outputs: dict[str, dict[str, Any]],
        parameters: dict[str, dict[str, Any]],
        api: FreeAtHomeApi,
    ) -> None:
        """Initialize the Free@Home Switch class."""
        super().__init__(device_id, channel_id, name, inputs, outputs, parameters, api)

    @property
    def state(self):
        """Get the state of the switch."""
        if self._state is None:
            _switch_output_id, _switch_output_value = self.get_output_by_pairing_id(
                pairing_id=PairingId.AL_INFO_ON_OFF.value
            )
            self._state = _switch_output_value == "1"

        return self._state

    @state.setter
    def state(self, value: bool):
        """Set the state of the switch."""
        _switch_input_id, _switch_input_value = self.get_input_by_pairing_id(
            pairing_id=PairingId.AL_SWITCH_ON_OFF.value
        )
        self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_switch_input_id,
            value="1" if value else "0",
        )
        self._state = value

    def refresh_state(self):
        """Refresh the state of the switch from the api."""
        _switch_output_id, _switch_output_value = self.get_output_by_pairing_id(
            pairing_id=PairingId.AL_INFO_ON_OFF.value
        )

        _datapoint = self._api.get_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_switch_output_id,
        )[0]

        self._state = _datapoint == "1"


if __name__ == "__main__":
    pass
