"""Provides a class for interacting with the ABB-free@home API."""

import asyncio
from collections.abc import Callable
import inspect
import json
import logging
import os
from typing import Any
from urllib.parse import urlparse

from aiohttp.client import ClientSession, ClientWebSocketResponse
from aiohttp.client_exceptions import (
    ClientConnectionError as AioHttpClientConnectionError,
    ClientResponseError as AioHttpClientResponseError,
    InvalidUrlClientError as AioHttpInvalidUrlClientError,
    WSServerHandshakeError as AioHttpWSServerHandshakeError,
)
from aiohttp.helpers import BasicAuth
from aiohttp.http import WSMsgType
import backoff
from packaging.version import Version
import voluptuous as vol

from .exceptions import (
    BadRequestException,
    ClientConnectionError,
    ConnectionTimeoutException,
    ForbiddenAuthException,
    InvalidApiResponseException,
    InvalidCredentialsException,
    InvalidHostException,
    SetDatapointFailureException,
    UserNotFoundException,
)

API_VERSION = "v1"

# API Requests Configuration
DEFAULT_FREEATHOME_MAX_REQUEST_TRIES = 5

VIRTUAL_DEVICE_ROOT_SCHEMA = vol.Schema(
    {
        vol.Required("type"): str,
    }
)

VIRTUAL_DEVICE_PROPERTIES_SCHEMA = vol.Schema(
    {
        vol.Required("ttl"): vol.All(
            vol.Coerce(int),
            vol.Any(vol.Range(min=-1, max=0), vol.Range(min=180, max=86400)),
        ),
        vol.Optional("displayname"): str,
        vol.Inclusive("flavor", "flavor_capabilities"): str,
        vol.Inclusive("capabilities", "flavor_capabilities"): [int],
    }
)

_LOGGER = logging.getLogger(__name__)


class FreeAtHomeSettings:
    """Provides a class for fetching the settings from a ABB free@home SysAP."""

    _client_session: ClientSession = None
    _close_client_session: bool = False
    _settings: dict = None

    def __init__(self, host: str, client_session: ClientSession = None) -> None:
        """Initialize the FreeAtHomeSettings class."""
        self._host: str = host
        self._client_session: ClientSession = client_session

    async def __aenter__(self):
        """Async enter and return self."""
        return self

    async def __aexit__(self, *_exc_info: object):
        """Close client session connections."""
        await self.close_client_session()

    async def close_client_session(self):
        """Close the client session if created by FreeAtHomeSettings."""
        if self._client_session and self._close_client_session:
            await self._client_session.close()

    async def load(self):
        """Load settings into the class object."""
        try:
            async with (
                self._get_client_session().get(f"{self._host}/settings.json") as resp,
            ):
                _response_status = resp.status
                _response_json = await resp.json()
        except AioHttpInvalidUrlClientError as e:
            raise InvalidHostException(self._host) from e
        except AioHttpClientConnectionError as e:
            raise ClientConnectionError(self._host) from e

        assert _response_status == 200

        self._settings = _response_json

    def get_user(self, name: str) -> str:
        """Get a specific user from the api."""
        _user = next(
            iter(
                user for user in self._settings.get("users") if user.get("name") == name
            ),
            None,
        )

        if _user is None:
            raise UserNotFoundException(name)

        return _user

    def get_flag(self, name: str) -> Any:
        """Get a flag from the settings response."""
        return self._settings.get("flags").get(name)

    @property
    def has_api_support(self):
        """Get whether the SysAp has API support."""
        return Version(self.version) >= Version("2.6.0")

    @property
    def hardware_version(self):
        """Get the hardware vesion running on SysAP."""
        return self.get_flag("hardwareVersion")

    @property
    def version(self):
        """Get the vesion running on SysAP."""
        return self.get_flag("version")

    @property
    def serial_number(self):
        """Get the vesion running on SysAP."""
        return self.get_flag("serialNumber")

    @property
    def name(self):
        """Get the vesion running on SysAP."""
        return self.get_flag("name")

    def _get_client_session(self) -> ClientSession:
        """Get the aiohttp ClientSession object."""
        if self._client_session is None:
            self._client_session = ClientSession()
            self._close_client_session = True

        return self._client_session


class FreeAtHomeApi:
    """Provides a class for interacting with the ABB-free@home API."""

    _client_session: ClientSession = None
    _close_client_session: bool = False
    _ws_response: ClientWebSocketResponse = None

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        sysap_uuid: str = "00000000-0000-0000-0000-000000000000",
        client_session: ClientSession = None,
        ws_heartbeat: int = 30,
    ) -> None:
        """Initialize the FreeAtHomeApi class."""
        self._host = host.rstrip("/")
        self._auth = BasicAuth(username, password)
        self._sysap_uuid = sysap_uuid
        self._client_session = client_session
        self._ws_heartbeat = ws_heartbeat

    async def __aenter__(self):
        """Async enter and return self."""
        return self

    async def __aexit__(self, *_exc_info: object):
        """Close client session connections."""
        await self.ws_close()
        await self.close_client_session()

    async def close_client_session(self):
        """Close the client session if created by FreeAtHome."""
        if self._client_session and self._close_client_session:
            await self._client_session.close()

    async def get_configuration(self) -> dict:
        """Get the Free@Home Configuration."""
        _response = await self._request(path="/api/rest/configuration")

        return _response.get(self._sysap_uuid)

    async def get_datapoint(
        self, device_serial: str, channel_id: str, datapoint: str
    ) -> list[str]:
        """Get a specific datapoint from the api."""
        _response = await self._request(
            path=f"/api/rest/datapoint/{self._sysap_uuid}/{device_serial}.{channel_id}.{datapoint}",
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

    async def get_sysap(self):
        """Get the sysap from the api."""
        return await self._request(path="/api/rest/sysap")

    async def set_datapoint(
        self, device_serial: str, channel_id: str, datapoint: str, value: str
    ) -> bool:
        """Set a specific datapoint in the api. This is used to control channels."""
        _response = await self._request(
            path=f"/api/rest/datapoint/{self._sysap_uuid}/{device_serial}.{channel_id}.{datapoint}",
            method="put",
            data=value,
        )

        if _response.get(self._sysap_uuid).get("result").lower() != "ok":
            raise SetDatapointFailureException(
                device_serial, channel_id, datapoint, value
            )

        return True

    async def virtualdevice(self, serial: str, data: dict[str, Any]):
        """Create or modify a virtualdevice in the api."""
        _schema = VIRTUAL_DEVICE_ROOT_SCHEMA.extend(
            {vol.Required("properties"): VIRTUAL_DEVICE_PROPERTIES_SCHEMA}
        )
        _schema(data)
        data["properties"]["ttl"] = str(data["properties"]["ttl"])
        _response = await self._request(
            path=f"/api/rest/virtualdevice/{self._sysap_uuid}/{serial}",
            method="put",
            data=json.dumps(data),
        )

        _key, _items = list(_response[self._sysap_uuid]["devices"].items())[0]
        return {serial: _key}

    def _get_client_session(self) -> ClientSession:
        """Get the ClientSession aiohttp object."""
        if self._client_session is None:
            self._client_session = ClientSession()
            self._close_client_session = True

        return self._client_session

    @backoff.on_exception(
        backoff.expo,
        InvalidApiResponseException,
        max_tries=int(
            os.environ.get(
                "FREEATHOME_MAX_REQUEST_TRIES", DEFAULT_FREEATHOME_MAX_REQUEST_TRIES
            )
        ),
    )
    async def _request(self, path: str, method: str = "get", data: Any | None = None):
        """Make a request to the API."""

        # Set the full path to be used.
        if path[0] != "/":
            path = f"/{path}"
        _full_path = f"/fhapi/{API_VERSION}{path}"

        try:
            async with (
                self._get_client_session().request(
                    method=method,
                    url=f"{self._host}{_full_path}",
                    data=data,
                    auth=self._auth,
                    raise_for_status=True,
                ) as resp,
            ):
                _response_status = resp.status
                _response_data = None
                if resp.content_type == "application/json":
                    _response_data = await resp.json()
                elif resp.content_type == "text/plain":
                    _response_data = await resp.text()
        except AioHttpInvalidUrlClientError as e:
            raise InvalidHostException(self._host) from e
        except AioHttpClientConnectionError as e:
            raise ClientConnectionError(self._host) from e
        except AioHttpClientResponseError as e:
            if e.status == 400:
                raise BadRequestException(data) from e
            if e.status == 401:
                raise InvalidCredentialsException(self._auth.login) from e
            if e.status == 403:
                raise ForbiddenAuthException(path, e.status) from e
            if e.status == 502:
                raise ConnectionTimeoutException(self._host) from e
            raise InvalidApiResponseException(e.status) from e

        return _response_data

    @property
    def ws_connected(self) -> bool:
        """Returns whether the websocket is connected."""
        return self._ws_response is not None and not self._ws_response.closed

    async def ws_close(self):
        """Close the websocket session."""
        await self.ws_disconnect()

    async def ws_connect(self):
        """Connect to the host websocket."""
        if self.ws_connected:
            return

        _parsed_host = urlparse(self._host)
        _full_path = f"{_parsed_host.hostname}/fhapi/{API_VERSION}/api/ws"
        _url = f"ws://{_full_path}"

        _LOGGER.info("Websocket attempting to connect %s", _url)
        self._ws_response = await self._get_client_session().ws_connect(
            url=_url, heartbeat=self._ws_heartbeat, auth=self._auth
        )
        _LOGGER.info("Websocket connected %s", _url)

    async def ws_disconnect(self):
        """Close the websockets connection."""
        if not self._ws_response or not self.ws_connected:
            return

        await self._ws_response.close()

    async def ws_listen(
        self, callback: Callable[[list], None] | None = None, retry_interval: int = 5
    ):  # pragma: no cover
        """Listen for events on the websocket."""
        while True:
            await self.ws_receive(callback, retry_interval)

    async def ws_receive(
        self, callback: Callable[[list], None] | None = None, retry_interval: int = 5
    ):
        """Receive an event on the websocket."""
        if not self._ws_response or not self.ws_connected:
            try:
                await self.ws_connect()
            except AioHttpWSServerHandshakeError:
                _LOGGER.exception("Websocket Handshake Connection Error.")
                await asyncio.sleep(retry_interval)
                return
            except AioHttpClientConnectionError:
                _LOGGER.exception("Websocket Client Connection Error.")
                await asyncio.sleep(retry_interval)
                return
            except TimeoutError:
                _LOGGER.exception("Timeout waiting for host.")
                await asyncio.sleep(retry_interval)
                return

        data = await self._ws_response.receive()
        if data.type == WSMsgType.TEXT:
            _ws_data = data.json().get(self._sysap_uuid)

            _LOGGER.debug("Websocket Response: %s", _ws_data)
            if callback and inspect.iscoroutinefunction(callback):
                await callback(_ws_data)
            elif callback:
                callback(_ws_data)
        elif data.type == WSMsgType.ERROR:
            _LOGGER.error("Websocket Response Error. Data: %s", data)
            await asyncio.sleep(retry_interval)
        elif data.type in (
            WSMsgType.CLOSE,
            WSMsgType.CLOSED,
            WSMsgType.CLOSING,
        ):
            _LOGGER.warning("Websocket Connection Closed.")
