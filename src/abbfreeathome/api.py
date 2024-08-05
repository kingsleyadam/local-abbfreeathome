import requests

from typing import List, Dict

from .bin.exceptions import UserNotFoundException, SetDatapointFailureException, InvalidCredentialsException

API_VERSION = 'v1'


class FreeAtHomeApi:
    def __init__(
            self,
            host: str,
            username: str,
            password: str,
            sysap_uuid: str = '00000000-0000-0000-0000-000000000000'
    ):
        self._sysap_uuid = sysap_uuid
        self._host = host.rstrip('/')
        self._username = username
        self._password = password

    def get_configuration(self) -> Dict:
        return self.request(
            path='/api/rest/configuration'
        ).get(self._sysap_uuid)

    def get_datapoint(self, device_id: str, channel_id: str, datapoint: str) -> List[str]:
        _response = self.request(
            path=f'/api/rest/datapoint/{self._sysap_uuid}/{device_id}.{channel_id}.{datapoint}',
            method='get'
        )

        return _response.get(self._sysap_uuid).get('values')

    def get_device_list(self) -> List:
        return self.request(
            path='/api/rest/devicelist'
        ).get(self._sysap_uuid)

    def get_device(self, device_serial: str):
        return self.request(
            path=f'/api/rest/device/{self._sysap_uuid}/{device_serial}'
        ).get(self._sysap_uuid).get('devices').get(device_serial)

    def get_device_data_point(self, device_serial: str, channel: str, datapoint: str):
        return self.request(
            path=f'/api/rest/datapoint/{self._sysap_uuid}/{device_serial}.{channel}.{datapoint}'
        ).get(self._sysap_uuid)

    def get_settings(self):
        _response = requests.request(
            method='get',
            url=f'{self._host}/settings.json',
        )
        _response.raise_for_status()

        return _response.json()

    def get_sysap(self):
        return self.request(
            path=f'/api/rest/sysap'
        )

    def get_user(self, name: str) -> str:
        _settings = self.get_settings()

        _user = next(
            iter(user for user in _settings.get('users')
            if user.get('name') == name),
            None
        )

        if _user is None:
            raise UserNotFoundException(f'User not found; {name}.')

        return _user

    def set_datapoint(self, device_id: str, channel_id: str, datapoint: str, value: str) -> bool:
        _response = self.request(
            path=f'/api/rest/datapoint/{self._sysap_uuid}/{device_id}.{channel_id}.{datapoint}',
            method='put',
            data=value
        )

        if _response.get(self._sysap_uuid).get('result').lower() != 'ok':
            raise SetDatapointFailureException(
                (
                    f'Failed to set datapoint; device_id: '
                    f'{device_id}; '
                    f'channel_id: {channel_id}; '
                    f'datapoint: {datapoint}; '
                    f'value: {value}'
                )
            )

        return True

    def request(self, path, method: str = 'get', data: any = None):
        _root_path = f'/fhapi/{API_VERSION}'
        _response = requests.request(
            method=method,
            url=f'{self._host}{_root_path}{path}',
            auth=(self._username, self._password),
            data=data
        )

        try:
            _response.raise_for_status()
        except requests.exceptions.HTTPError as http_exception:
            if http_exception.response.status_code == 401:
                raise InvalidCredentialsException(f'Invalid credentials for user: {self._username}')
            else:
                raise http_exception

        return _response.json()


if __name__ == '__main__':
    pass
