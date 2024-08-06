"""Provides a class for interacting with the ABB-free@home API."""

from typing import Any

import requests

from .exceptions import (
    InvalidCredentialsException,
    InvalidURLSchemaException,
    SetDatapointFailureException,
    UserNotFoundException,
)

API_VERSION = "v1"


class FreeAtHomeApi:
    """Provides a class for interacting with the ABB-free@home API."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        sysap_uuid: str = "00000000-0000-0000-0000-000000000000",
    ) -> None:
        """Initialize the FreeAtHomeApi class."""
        self._sysap_uuid = sysap_uuid
        self._host = host.rstrip("/")
        self._username = username
        self._password = password

    def get_configuration(self) -> dict:
        """Get the Free@Home Configuration."""
        return self._request(path="/api/rest/configuration").get(self._sysap_uuid)

    def get_datapoint(
        self, device_id: str, channel_id: str, datapoint: str
    ) -> list[str]:
        """Get a specific datapoint from the api."""
        _response = self._request(
            path=f"/api/rest/datapoint/{self._sysap_uuid}/{device_id}.{channel_id}.{datapoint}",
            method="get",
        )

        return _response.get(self._sysap_uuid).get("values")

    def get_device_list(self) -> list:
        """Get the list of devices."""
        return self._request(path="/api/rest/devicelist").get(self._sysap_uuid)

    def get_device(self, device_serial: str):
        """Get a specific device from the api."""
        return (
            self._request(path=f"/api/rest/device/{self._sysap_uuid}/{device_serial}")
            .get(self._sysap_uuid)
            .get("devices")
            .get(device_serial)
        )

    async def get_settings(self):
        """Get the settings from the api."""
        try:
            _response = requests.request(
                method="get", url=f"{self._host}/settings.json", timeout=10
            )
        except requests.exceptions.MissingSchema as ex:
            raise InvalidURLSchemaException(self._host) from ex

        _response.raise_for_status()
        return _response.json()

    async def get_sysap(self):
        """Get the sysap from the api."""
        return self._request(path="/api/rest/sysap")

    async def get_user(self, name: str) -> str:
        """Get a specific user from the api."""
        _settings = await self.get_settings()

        _user = next(
            iter(user for user in _settings.get("users") if user.get("name") == name),
            None,
        )

        if _user is None:
            raise UserNotFoundException(name)

        return _user

    def set_datapoint(
        self, device_id: str, channel_id: str, datapoint: str, value: str
    ) -> bool:
        """Set a specific datapoint in the api. This is used to control devices."""
        _response = self._request(
            path=f"/api/rest/datapoint/{self._sysap_uuid}/{device_id}.{channel_id}.{datapoint}",
            method="put",
            data=value,
        )

        if _response.get(self._sysap_uuid).get("result").lower() != "ok":
            raise SetDatapointFailureException(device_id, channel_id, datapoint, value)

        return True

    def _request(self, path, method: str = "get", data: Any | None = None):
        """Make a request to the API."""
        _root_path = f"/fhapi/{API_VERSION}"
        try:
            _response = requests.request(
                method=method,
                url=f"{self._host}{_root_path}{path}",
                auth=(self._username, self._password),
                data=data,
                timeout=10,
            )
        except requests.exceptions.MissingSchema as ex:
            raise InvalidURLSchemaException(self._host) from ex

        try:
            _response.raise_for_status()
        except requests.exceptions.HTTPError as http_exception:
            _unauthozied_code = 401
            if http_exception.response.status_code == _unauthozied_code:
                raise InvalidCredentialsException(self._username) from http_exception
            raise
        return _response.json()


if __name__ == "__main__":
    pass
