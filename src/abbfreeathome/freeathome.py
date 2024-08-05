from typing import Dict, List

from .api import FreeAtHomeApi
from .bin.function_id import FunctionID
from .devices.switch import Switch


class FreeAtHome:
    _config = None

    def __init__(self, api: FreeAtHomeApi):
        self._api = api

    @property
    def floors(self) -> Dict:
        return self.get_config().get('floorplan').get('floors')

    @property
    def switches(self) -> List[Switch]:
        _devices = self.get_devices_by_function(function_id=FunctionID.FID_SWITCH_ACTUATOR.value)
        _switches = list()
        for _device in _devices:
            _switches.append(
                Switch(
                    device_id=_device.get('device_id'),
                    channel_id=_device.get('channel_id'),
                    name=_device.get('name'),
                    inputs=_device.get('inputs'),
                    outputs=_device.get('outputs'),
                    parameters=_device.get('parameters'),
                    api=self._api
                )
            )

        return _switches

    def get_config(self, refresh: bool = False) -> Dict:
        if self._config is None or refresh:
            self._config = self._api.get_configuration()

        return self._config

    def get_devices_by_function(self, function_id: str) -> List[dict]:
        _devices = list()
        for _device_key, _device in self.get_config().get('devices').items():
            for _channel_key, _channel in _device.get('channels', dict()).items():
                if _channel.get('functionID') == function_id:
                    _name = _channel.get('displayName')
                    if _name == 'Ⓐ' or _name is None:
                        _name = _device.get('displayName')

                    _devices.append(
                        dict(
                            device_id=_device_key,
                            channel_id=_channel_key,
                            name=_name,
                            function_id=_channel.get('functionID'),
                            floor_name=self.get_floor_name(
                                floor_serial_id=_channel.get('floor', _device.get('floor'))
                            ),
                            room_name=self.get_room_name(
                                floor_serial_id=_channel.get('floor', _device.get('floor')),
                                room_serial_id=_channel.get('room', _device.get('room'))
                            ),
                            inputs=_channel.get('inputs'),
                            outputs=_channel.get('outputs'),
                            parameters=_channel.get('parameters'),
                        )
                    )

        return _devices

    def get_floor_name(self, floor_serial_id: str) -> str:
        _default_room = dict(name='unknown', rooms=dict())
        return self.floors.get(floor_serial_id, _default_room).get('name')

    def get_room_name(self, floor_serial_id: str, room_serial_id: str) -> str:
        _default_room = dict(name='unknown', rooms=dict())
        return self.floors.get(floor_serial_id, _default_room).get('rooms').get(room_serial_id).get('name', 'unknown')


if __name__ == '__main__':
    pass
