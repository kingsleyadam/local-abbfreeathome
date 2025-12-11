"""Provides a class for interacting with the ABB-free@home API."""

import asyncio
from collections.abc import Callable
import inspect
import json
import logging
import os
import ssl
from typing import Any
from urllib.parse import urlparse

from aiohttp import TCPConnector
from aiohttp.client import ClientSession, ClientWebSocketResponse
from aiohttp.client_exceptions import (
    ClientConnectionError as AioHttpClientConnectionError,
    ClientResponseError as AioHttpClientResponseError,
    ClientSSLError as AioClientSSLError,
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
    SslErrorException,
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


class SSLContextMixin:
    """Mixin class to provide SSL context functionality."""

    def __init__(self):
        """Initialize the SSL context mixin."""
        self._ssl_context: ssl.SSLContext | bool | None = None

    def _create_ssl_context_sync(self, cafile: str) -> ssl.SSLContext:
        """Create SSL context synchronously (for use in executor)."""
        return ssl.create_default_context(cafile=cafile)

    async def _get_ssl_context(self) -> ssl.SSLContext | bool:
        """Get the SSL context for requests."""
        if self._ssl_context is not None:
            return self._ssl_context

        if not self._verify_ssl:
            self._ssl_context = False
        elif self._ssl_cert_ca_file:
            # Run SSL context creation in executor to avoid blocking the event loop
            loop = asyncio.get_running_loop()
            self._ssl_context = await loop.run_in_executor(
                None, self._create_ssl_context_sync, self._ssl_cert_ca_file
            )
        else:
            self._ssl_context = True

        return self._ssl_context


class FreeAtHomeSettings(SSLContextMixin):
    """Provides a class for fetching the settings from a ABB free@home SysAP."""

    _client_session: ClientSession = None
    _close_client_session: bool = False
    _settings: dict = None

    def __init__(
        self,
        host: str,
        client_session: ClientSession = None,
        verify_ssl: bool = True,
        ssl_cert_ca_file: str | None = None,
    ) -> None:
        """Initialize the FreeAtHomeSettings class."""
        super().__init__()
        self._host: str = host
        self._client_session: ClientSession = client_session
        self._verify_ssl: bool = verify_ssl
        self._ssl_cert_ca_file: str | None = ssl_cert_ca_file

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
        ssl_context = await self._get_ssl_context()
        try:
            async with (
                self._get_client_session().get(
                    f"{self._host}/settings.json", ssl=ssl_context
                ) as resp,
            ):
                _response_status = resp.status
                _response_json = await resp.json()
        except AioHttpInvalidUrlClientError as e:
            raise InvalidHostException(self._host) from e
        except AioClientSSLError as e:
            raise SslErrorException(self._host) from e
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
            _tcp_connector = TCPConnector(
                limit=10,
                limit_per_host=5,
                ttl_dns_cache=300,
            )
            self._client_session = ClientSession(connector=_tcp_connector)
            self._close_client_session = True

        return self._client_session


class FreeAtHomeApi(SSLContextMixin):
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
        verify_ssl: bool = True,
        ssl_cert_ca_file: str | None = None,
        wait_for_result: bool = True,
    ) -> None:
        """
        Initialize the FreeAtHomeApi class.

        Args:
            host: The hostname or IP address of the SysAP.
            username: The username for authentication.
            password: The password for authentication.
            sysap_uuid: The UUID of the SysAP.
                Defaults to "00000000-0000-0000-0000-000000000000".
            client_session: An existing aiohttp ClientSession.
                Defaults to None.
            ws_heartbeat: Interval for websocket heartbeat in seconds.
                Defaults to 30.
            verify_ssl: Whether to verify SSL certificates.
                Defaults to True.
            ssl_cert_ca_file: Path to custom CA file for SSL verification.
                Defaults to None.
            wait_for_result: Controls whether to wait for API response
                (True) or use fire-and-forget mode (False). If set to
                False, relies on websocket for state updates and errors
                are only logged. Defaults to True.

        Note:
            When using fire-and-forget mode (i.e.,
            ``wait_for_result=False``), background tasks may be created
            to handle API requests. Before closing the API instance, you
            must ensure that all pending background tasks are properly
            awaited or cancelled to avoid resource leaks. This can be
            done by using the API instance as an async context manager
            (i.e., via ``async with`` which calls ``__aexit__``), or by
            explicitly calling ``close_client_session()`` before program
            exit.

        """
        super().__init__()
        self._host = host.rstrip("/")
        self._auth = BasicAuth(username, password)
        self._headers = {"Authorization": self._auth.encode()}
        self._sysap_uuid = sysap_uuid
        self._client_session = client_session
        self._ws_heartbeat = ws_heartbeat
        self._verify_ssl: bool = verify_ssl
        self._ssl_cert_ca_file: None | str = ssl_cert_ca_file
        self._background_tasks: set[asyncio.Task] = set()
        self._wait_for_result = wait_for_result

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
        self,
        device_serial: str,
        channel_id: str,
        datapoint: str,
        value: str,
        wait_for_result: bool | None = None,
    ) -> bool:
        """
        Set a specific datapoint in the API to control channels.

        Args:
            device_serial: The serial number of the device.
            channel_id: The channel ID of the device.
            datapoint: The datapoint to set.
            value: The value to set for the datapoint.
            wait_for_result: Overrides the class-level setting to
                control whether to wait for the API response. If None
                (default), uses the class-level setting. Set to False
                for better performance when websocket updates are
                available, as the method will not wait for the API
                response and will rely on websocket updates. Set to
                True to wait for the API response before returning.

        Returns:
            bool: True if the request was sent.

        """
        if wait_for_result is None:
            wait_for_result = self._wait_for_result

        if wait_for_result:
            await self._set_datapoint_request(
                device_serial, channel_id, datapoint, value
            )
            return True

        # We don't want to wait for the api to return our request, instead send the
        # request off into a background task and rely on the websocket for updates
        task = asyncio.create_task(
            self._set_datapoint_background(device_serial, channel_id, datapoint, value),
            name=f"set_datapoint_{device_serial}_{channel_id}_{datapoint}",
        )
        self._background_tasks.add(task)
        task.add_done_callback(self._set_datapoint_done_callback)
        return True

    def _set_datapoint_done_callback(self, task: asyncio.Task) -> None:
        """Handle cleanup when a background task completes."""
        self._background_tasks.discard(task)
        _LOGGER.debug(
            "Background task '%s' completed and removed from tracking set",
            task.get_name(),
        )

    async def _set_datapoint_background(
        self, device_serial: str, channel_id: str, datapoint: str, value: str
    ):
        """Set a specific datapoint in the api in the background."""
        try:
            await self._set_datapoint_request(
                device_serial, channel_id, datapoint, value
            )
        except Exception:  # noqa: BLE001
            _LOGGER.exception(
                "Failed to set datapoint %s/%s/%s",
                device_serial,
                channel_id,
                datapoint,
            )

    async def _set_datapoint_request(
        self, device_serial: str, channel_id: str, datapoint: str, value: str
    ):
        """Set a specific datapoint in the api."""
        _response = await self._request(
            path=f"/api/rest/datapoint/{self._sysap_uuid}/{device_serial}.{channel_id}.{datapoint}",
            method="put",
            data=value,
        )

        if _response.get(self._sysap_uuid).get("result").lower() != "ok":
            raise SetDatapointFailureException(
                device_serial, channel_id, datapoint, value
            )

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
            _tcp_connector = TCPConnector(
                limit=10,
                limit_per_host=5,
                ttl_dns_cache=300,
            )
            self._client_session = ClientSession(connector=_tcp_connector)
            self._close_client_session = True

        return self._client_session

    def _handle_response_error(
        self, error: AioHttpClientResponseError, data: Any, path: str
    ):
        """Handle response errors."""
        if error.status == 400:
            raise BadRequestException(data) from error
        if error.status == 401:
            raise InvalidCredentialsException(self._auth.login) from error
        if error.status == 403:
            raise ForbiddenAuthException(path, error.status) from error
        if error.status == 502:
            raise ConnectionTimeoutException(self._host) from error
        raise InvalidApiResponseException(error.status) from error

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

        ssl_context = await self._get_ssl_context()

        try:
            async with (
                self._get_client_session().request(
                    method=method,
                    url=f"{self._host}{_full_path}",
                    data=data,
                    headers=self._headers,
                    raise_for_status=True,
                    ssl=ssl_context,
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
        except AioClientSSLError as e:
            raise SslErrorException(self._host) from e
        except AioHttpClientConnectionError as e:
            raise ClientConnectionError(self._host) from e
        except AioHttpClientResponseError as e:
            self._handle_response_error(e, data, path)

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
        _protocol = "wss" if _parsed_host.scheme == "https" else "ws"
        _full_path = f"{_parsed_host.hostname}/fhapi/{API_VERSION}/api/ws"
        _url = f"{_protocol}://{_full_path}"

        ssl_context = await self._get_ssl_context()

        _LOGGER.info("Websocket attempting to connect %s", _url)
        self._ws_response = await self._get_client_session().ws_connect(
            url=_url,
            heartbeat=self._ws_heartbeat,
            headers=self._headers,
            ssl=ssl_context,
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
            except AioClientSSLError as e:
                raise SslErrorException(self._host) from e
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
