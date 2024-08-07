"""Provides a class for interacting with the ABB-free@home API."""

from typing import Any

import aiohttp

from .exceptions import (
    ConnectionTimeoutException,
    ForbiddenAuthException,
    InvalidApiResponseException,
    InvalidCredentialsException,
    InvalidHostException,
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

    async def get_configuration(self) -> dict:
        """Get the Free@Home Configuration."""
        _response = await self._request(path="/api/rest/configuration")

        return _response.get(self._sysap_uuid)

    async def get_datapoint(
        self, device_id: str, channel_id: str, datapoint: str
    ) -> list[str]:
        """Get a specific datapoint from the api."""
        _response = await self._request(
            path=f"/api/rest/datapoint/{self._sysap_uuid}/{device_id}.{channel_id}.{datapoint}",
            method="get",
        )

        return _response.get(self._sysap_uuid).get("values")

    async def get_device_list(self) -> list:
        """Get the list of devices."""
        _response = await self._request(path="/api/rest/devicelist")

        return _response.get(self._sysap_uuid)

    async def get_device(self, device_serial: str):
        """Get a specific device from the api."""
        _response = await self._request(
            path=f"/api/rest/device/{self._sysap_uuid}/{device_serial}"
        )

        return _response.get(self._sysap_uuid).get("devices").get(device_serial)

    async def get_settings(self):
        """Get the settings from the api."""
        try:
            async with aiohttp.ClientSession() as session:  # noqa: SIM117
                async with session.get(f"{self._host}/settings.json") as resp:
                    _response_status = resp.status
                    _response_json = await resp.json()
        except ValueError as e:
            if str(e) == "URL should be absolute":
                raise InvalidHostException(self._host) from e
            raise

        assert _response_status == 200
        return _response_json

    async def get_sysap(self):
        """Get the sysap from the api."""
        return await self._request(path="/api/rest/sysap")

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

    async def set_datapoint(
        self, device_id: str, channel_id: str, datapoint: str, value: str
    ) -> bool:
        """Set a specific datapoint in the api. This is used to control devices."""
        _response = await self._request(
            path=f"/api/rest/datapoint/{self._sysap_uuid}/{device_id}.{channel_id}.{datapoint}",
            method="put",
            data=value,
        )

        if _response.get(self._sysap_uuid).get("result").lower() != "ok":
            raise SetDatapointFailureException(device_id, channel_id, datapoint, value)

        return True

    async def _request(self, path: str, method: str = "get", data: Any | None = None):
        """Make a request to the API."""

        # Set the full path to be used.
        if path[0] != "/":
            path = f"/{path}"
        _full_path = f"/fhapi/{API_VERSION}{path}"

        try:
            async with aiohttp.ClientSession(  # noqa: SIM117
                base_url=self._host,
                auth=aiohttp.BasicAuth(self._username, self._password),
            ) as client:
                async with client.request(
                    method=method, url=_full_path, data=data
                ) as resp:
                    _response_status = resp.status
                    _response = None
                    if resp.content_type == "application/json":
                        _response = await resp.json()
                    elif resp.content_type == "text/plain":
                        _response = await resp.text()
        except ValueError as e:
            if str(e) == "URL should be absolute":
                raise InvalidHostException(self._host) from e
            raise

        # Check the status code and raise exception accordingly.
        _unauthozied_code = 401
        _forbidden_code = 403
        _connect_timeout_code = 502
        if _response_status == _unauthozied_code:
            raise InvalidCredentialsException(self._username)
        if _response_status == _forbidden_code:
            raise ForbiddenAuthException(path)
        if _response_status == _connect_timeout_code:
            raise ConnectionTimeoutException(self._host)

        try:
            assert _response_status == 200
        except AssertionError:
            raise InvalidApiResponseException(_response_status) from None

        return _response


if __name__ == "__main__":
    pass
