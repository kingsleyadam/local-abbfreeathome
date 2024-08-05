from typing import Dict

from .base import Base
from ..bin.pairing_id import PairingId
from ..api import FreeAtHomeApi


class Switch(Base):
    _state = None

    def __init__(
            self,
            device_id: str,
            channel_id: str,
            name: str,
            inputs: Dict[str, Dict[str, any]],
            outputs: Dict[str, Dict[str, any]],
            parameters: Dict[str, Dict[str, any]],
            api: FreeAtHomeApi
    ):
        super().__init__(device_id, channel_id, name, inputs, outputs, parameters, api)

    @property
    def state(self):
        if self._state is None:
            _switch_output_id, _switch_output_value = self.get_output_by_pairing_id(
                pairing_id=PairingId.AL_INFO_ON_OFF.value
            )
            self._state = '1' == _switch_output_value

        return self._state

    @state.setter
    def state(self, value: bool):
        _switch_input_id, _switch_input_value = self.get_input_by_pairing_id(
            pairing_id=PairingId.AL_SWITCH_ON_OFF.value
        )
        self._api.set_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_switch_input_id,
            value='1' if value else '0'
        )
        self._state = value

    def refresh_state(self):
        _switch_output_id, _switch_output_value = self.get_output_by_pairing_id(
            pairing_id=PairingId.AL_INFO_ON_OFF.value
        )

        _datapoint = self._api.get_datapoint(
            device_id=self.device_id,
            channel_id=self.channel_id,
            datapoint=_switch_output_id
        )[0]

        self._state = '1' == _datapoint


if __name__ == '__main__':
    pass

