from typing import Union, Dict, Tuple

from ..api import FreeAtHomeApi


class Base:
    def __init__(
            self,
            device_id: str,
            channel_id: str,
            name: str,
            inputs: Dict[str, Dict[str, any]],
            outputs: Dict[str, Dict[str, any]],
            parameters: Dict[str, Dict[str, any]],
            api: Union[FreeAtHomeApi, None]
    ):
        self._device_id = device_id
        self._channel_id = channel_id
        self._name = name
        self._api = api
        self._inputs = inputs
        self._outputs = outputs
        self._parameters = parameters

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def channel_id(self) -> str:
        return self._channel_id

    @property
    def name(self) -> str:
        return self._name

    def get_input_by_pairing_id(self, pairing_id: int) -> Tuple[str, any]:
        for _input_id, _input in self._inputs.items():
            if _input.get('pairingID') == pairing_id:
                return _input_id, _input.get('value')

        raise ValueError(
            f'Could not find input for device: {self.device_id}; channel: {self.channel_id}; pairing id: {pairing_id}'
        )

    def get_output_by_pairing_id(self, pairing_id: int) -> Tuple[str, any]:
        for _output_id, _output in self._outputs.items():
            if _output.get('pairingID') == pairing_id:
                return _output_id, _output.get('value')

        raise ValueError(
            f'Could not find output for device: {self.device_id}; channel: {self.channel_id}; pairing id: {pairing_id}'
        )
