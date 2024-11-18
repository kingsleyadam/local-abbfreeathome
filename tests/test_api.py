"""Test code to test all FreeAtHome class."""

from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import aiohttp
from aioresponses import aioresponses
import pytest

from src.abbfreeathome.api import FreeAtHomeApi, FreeAtHomeSettings
from src.abbfreeathome.exceptions import (
    ClientConnectionError,
    ConnectionTimeoutException,
    ForbiddenAuthException,
    InvalidApiResponseException,
    InvalidCredentialsException,
    InvalidHostException,
    SetDatapointFailureException,
    UserNotFoundException,
)


@pytest.fixture
def api():
    """Create FreeAtHome Api Fixture."""
    return FreeAtHomeApi(host="http://192.168.1.1", username="user", password="pass")


@pytest.fixture
def settings():
    """Create FreeAtHome Api Fixture."""
    return FreeAtHomeSettings(host="http://192.168.1.1")


@pytest.mark.asyncio
async def test_settings_aenter_returns_instance(settings):
    """Test the __aenter__ function with own session."""
    async with settings as instance:
        assert instance is settings


@pytest.mark.asyncio
async def test_settings_aexit_closes_client_session(settings):
    """Test the __aexit__ function with own session."""
    mock_session = AsyncMock(spec=aiohttp.ClientSession)

    settings._client_session = mock_session
    settings._close_client_session = True  # Ensure the session should close

    # Call the __aexit__ method
    await settings.__aexit__(None, None, None)

    # Assert that the client session close method was called
    settings._client_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_load_success(settings):
    """Test loading settings into class."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.1/settings.json",
            payload={
                "users": [{"name": "test_user"}],
                "flags": {
                    "version": "1.0",
                    "serialNumber": "12345",
                    "name": "SysAP",
                    "hardwareVersion": "54321",
                },
            },
        )

        await settings.load()
        assert settings._settings == {
            "users": [{"name": "test_user"}],
            "flags": {
                "version": "1.0",
                "serialNumber": "12345",
                "name": "SysAP",
                "hardwareVersion": "54321",
            },
        }


@pytest.mark.asyncio
async def test_get_settings_invalid_host(settings):
    """Test the get_settings function for invalid host."""
    settings._host = "192.168.1.1"

    with pytest.raises(InvalidHostException):
        await settings.load()


@pytest.mark.asyncio
async def test_get_settings_client_connection_error(settings):
    """Test the _request function for an invalid client."""
    settings._host = "http://0.0.0.0:1"

    with pytest.raises(ClientConnectionError):
        await settings.load()


def test_get_user(settings):
    """Test getting a user."""
    settings._settings = {"users": [{"name": "test_user"}]}
    assert settings.get_user("test_user") == {"name": "test_user"}


def test_get_user_not_found(settings):
    """Test getting a user not found."""
    settings._settings = {"users": [{"name": "test_user"}]}
    with pytest.raises(UserNotFoundException):
        settings.get_user("non_existent_user")


def test_get_flag(settings):
    """Test getting a single flag."""
    settings._settings = {"flags": {"version": "1.0"}}
    assert settings.get_flag("version") == "1.0"


def test_has_api_support_property(settings):
    """Test getting has_api_support property."""
    settings._settings = {"flags": {"version": "1.0"}}
    assert settings.has_api_support is False

    settings._settings = {"flags": {"version": "2.6.0"}}
    assert settings.has_api_support is True


def test_hardware_version_property(settings):
    """Test getting hardware verison."""
    settings._settings = {"flags": {"hardwareVersion": "54321"}}
    assert settings.hardware_version == "54321"


def test_version_property(settings):
    """Test getting version."""
    settings._settings = {"flags": {"version": "1.0"}}
    assert settings.version == "1.0"


def test_serial_number_property(settings):
    """Test getting serial number."""
    settings._settings = {"flags": {"serialNumber": "12345"}}
    assert settings.serial_number == "12345"


def test_name_property(settings):
    """Test getting name."""
    settings._settings = {"flags": {"name": "SysAP"}}
    assert settings.name == "SysAP"


@pytest.mark.asyncio
async def test_aenter_returns_instance(api):
    """Test the __aenter__ function with own session."""
    async with api as instance:
        assert instance is api


@pytest.mark.asyncio
async def test_aexit_closes_client_session_and_websocket(api):
    """Test the __aexit__ function with own session."""
    mock_session = AsyncMock(spec=aiohttp.ClientSession)

    api._client_session = mock_session
    api._ws_response = AsyncMock()
    api._ws_response.closed = False
    api._close_client_session = True  # Ensure the session should close

    # Call the __aexit__ method
    await api.__aexit__(None, None, None)

    # Assert that the websocket close method was called
    api._ws_response.close.assert_awaited_once()

    # Assert that the client session close method was called
    api._client_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_aexit_does_not_close_client_session_when_not_needed(api):
    """Test the __aexit__ function with external session."""
    mock_session = AsyncMock(spec=aiohttp.ClientSession)

    api._client_session = mock_session
    api._ws_response = AsyncMock()
    api._ws_response.closed = False  # Ensure the websocket is initially open
    api._close_client_session = False  # Ensure the session should NOT close

    # Call the __aexit__ method
    await api.__aexit__(None, None, None)

    # Assert that the websocket close method was called
    api._ws_response.close.assert_awaited_once()

    # Assert that the client session close method was NOT called
    api._client_session.close.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_configuration(api):
    """Test the get_configuration function."""
    with patch.object(api, "_request", return_value=Mock()) as mock_request:
        mock_request.return_value.get.return_value = {}
        config = await api.get_configuration()
        assert config == {}


@pytest.mark.asyncio
async def test_get_datapoint(api):
    """Test the get_datapoint function."""
    with patch.object(api, "_request", return_value=Mock()) as mock_request:
        mock_request.return_value.get.return_value = {"values": ["value1", "value2"]}
        datapoint = await api.get_datapoint("device_id", "channel_id", "datapoint")
        assert datapoint == ["value1", "value2"]


@pytest.mark.asyncio
async def test_get_device_list(api):
    """Test the get_device_list function."""
    with patch.object(api, "_request", return_value=Mock()) as mock_request:
        mock_request.return_value.get.return_value = ["device1", "device2"]
        device_list = await api.get_device_list()
        assert device_list == ["device1", "device2"]


@pytest.mark.asyncio
async def test_get_device(api):
    """Test the get_device function."""
    with patch.object(api, "_request", return_value=Mock()) as mock_request:
        mock_request.return_value.get.return_value = {
            "devices": {"device_serial": "device_info"}
        }
        device = await api.get_device("device_serial")
        assert device == "device_info"


@pytest.mark.asyncio
async def test_get_sysap(api):
    """Test the get_sysap function."""
    with patch.object(api, "_request", return_value=Mock()) as mock_request:
        mock_request.return_value = {"sysap": "value"}
        sysap = await api.get_sysap()
        assert sysap == {"sysap": "value"}


@pytest.mark.asyncio
async def test_set_datapoint(api):
    """Test the set_datapoint function."""
    with patch.object(api, "_request", return_value=Mock()) as mock_request:
        mock_request.return_value.get.return_value = {"result": "ok"}
        result = await api.set_datapoint(
            "device_id", "channel_id", "datapoint", "value"
        )
        assert result is True


@pytest.mark.asyncio
async def test_set_datapoint_failure(api):
    """Test the set_datapoint function for failure."""
    with patch.object(api, "_request", return_value=Mock()) as mock_request:
        mock_request.return_value.get.return_value = {"result": "fail"}
        with pytest.raises(SetDatapointFailureException):
            await api.set_datapoint("device_id", "channel_id", "datapoint", "value")


@pytest.mark.asyncio
async def test_ws_connect(api):
    """Test the ws_connect function."""
    with patch("aiohttp.ClientSession.ws_connect", new_callable=AsyncMock):
        await api.ws_connect()


@pytest.mark.asyncio
async def test_ws_connect_already_connected(api):
    """Test the ws_connect function already connected."""
    with patch.object(
        FreeAtHomeApi, "ws_connected", new_callable=PropertyMock
    ) as mock_ws_connected:
        mock_ws_connected.return_value = True
        with patch(
            "aiohttp.ClientSession.ws_connect", new_callable=AsyncMock
        ) as mock_ws_connect:
            await api.ws_connect()
            mock_ws_connect.assert_not_called()


@pytest.mark.asyncio
async def test_ws_disconnect(api):
    """Test the ws_disconnect function."""
    with patch.object(
        FreeAtHomeApi, "ws_connected", new_callable=PropertyMock
    ) as mock_ws_connected:
        mock_ws_connected.return_value = True
        with patch.object(
            api, "_ws_response", new_callable=PropertyMock
        ) as mock_ws_response:
            mock_ws_response.return_value = AsyncMock()
            with patch.object(
                api._ws_response, "close", new_callable=AsyncMock
            ) as mock_close:
                await api.ws_disconnect()
                mock_close.assert_called_once()


@pytest.mark.asyncio
async def test_ws_disconnect_no_response(api):
    """Test the ws_disconnect function for no response."""
    with patch.object(
        FreeAtHomeApi, "ws_connected", new_callable=PropertyMock
    ) as mock_ws_connected:
        mock_ws_connected.return_value = True
        with patch.object(
            FreeAtHomeApi, "_ws_response", new_callable=PropertyMock
        ) as mock_ws_response:
            mock_ws_response.return_value = None
            await api.ws_disconnect()
            # Ensure no exception is raised and no call to close is made
            assert True


@pytest.mark.asyncio
async def test_ws_close(api):
    """Test the ws_close function."""
    with (
        patch.object(
            FreeAtHomeApi, "ws_disconnect", new_callable=AsyncMock
        ) as mock_ws_disconnect,
    ):
        await api.ws_close()
        mock_ws_disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_ws_receive(api):
    """Test the ws_receive function."""
    async_callback = AsyncMock()
    mock_callback = Mock()

    with (
        patch.object(
            FreeAtHomeApi, "ws_connected", new_callable=PropertyMock
        ) as mock_ws_connected,
        patch.object(
            FreeAtHomeApi, "_ws_response", new_callable=PropertyMock
        ) as mock_ws_response,
    ):
        mock_ws_connected.return_value = True
        mock_ws_response.return_value = Mock()
        mock_ws_response.return_value.receive = AsyncMock(
            return_value=Mock(
                type=aiohttp.WSMsgType.TEXT,
                json=Mock(return_value={api._sysap_uuid: "data"}),
            )
        )
        with patch("asyncio.sleep", new_callable=AsyncMock):
            # Check both async and non-async callbacks.
            await api.ws_receive(async_callback)
            async_callback.assert_called_once_with("data")

            await api.ws_receive(mock_callback)
            async_callback.assert_called_once_with("data")

    # Test Different Connection Errors
    api._ws_response = None
    callback = AsyncMock()
    with (
        patch(
            "aiohttp.ClientSession.ws_connect",
            side_effect=aiohttp.ClientConnectionError,
        ),
        patch("asyncio.sleep", new_callable=AsyncMock),
    ):
        await api.ws_receive(callback)
        callback.assert_not_called()

    with (
        patch(
            "aiohttp.ClientSession.ws_connect",
            side_effect=aiohttp.WSServerHandshakeError(request_info=Mock, history=Mock),
        ),
        patch("asyncio.sleep", new_callable=AsyncMock),
    ):
        await api.ws_receive(callback)
        callback.assert_not_called()

    with (
        patch(
            "aiohttp.ClientSession.ws_connect",
            side_effect=TimeoutError,
        ),
        patch("asyncio.sleep", new_callable=AsyncMock),
    ):
        await api.ws_receive(callback)
        callback.assert_not_called()


@pytest.mark.asyncio
async def test_ws_receive_closed(api):
    """Test the ws_receive function for closed connection."""
    async_callback = AsyncMock()
    with patch.object(
        FreeAtHomeApi, "ws_connected", new_callable=PropertyMock
    ) as mock_ws_connected:
        mock_ws_connected.return_value = True
        with patch.object(
            FreeAtHomeApi, "_ws_response", new_callable=PropertyMock
        ) as mock_ws_response:
            mock_ws_response.return_value = Mock()
            mock_ws_response.return_value.receive = AsyncMock(
                return_value=Mock(type=aiohttp.WSMsgType.CLOSE)
            )
            with patch("asyncio.sleep", new_callable=AsyncMock):
                await api.ws_receive(async_callback)
                async_callback.assert_not_called()


@pytest.mark.asyncio
async def test_ws_receive_error(api):
    """Test the ws_receive function for error response."""
    async_callback = AsyncMock()
    with patch.object(
        FreeAtHomeApi, "ws_connected", new_callable=PropertyMock
    ) as mock_ws_connected:
        mock_ws_connected.return_value = True
        with patch.object(
            FreeAtHomeApi, "_ws_response", new_callable=PropertyMock
        ) as mock_ws_response:
            mock_ws_response.return_value = Mock()
            mock_ws_response.return_value.receive = AsyncMock(
                return_value=Mock(type=aiohttp.WSMsgType.ERROR)
            )
            with patch("asyncio.sleep", new_callable=AsyncMock):
                await api.ws_receive(async_callback)
                async_callback.assert_not_called()


@pytest.mark.asyncio
async def test_request_success_json(api):
    """Test the _request function for json response."""
    with aioresponses() as m:
        m.get(
            f"{api._host}/fhapi/v1/test",
            payload={"key": "value"},
            status=200,
        )

        response = await api._request("test")

        assert response == {"key": "value"}


@pytest.mark.asyncio
async def test_request_success_text(api):
    """Test the _request function for text response."""
    with aioresponses() as m:
        m.get(
            f"{api._host}/fhapi/v1/test",
            body="plain text",
            status=200,
            content_type="text/plain",
        )

        response = await api._request("test")

        assert response == "plain text"


@pytest.mark.asyncio
async def test_request_invalid_host(api):
    """Test the _request function for invalid host."""
    api._host = "192.168.1.1"

    with pytest.raises(InvalidHostException):
        await api._request("/test")


@pytest.mark.asyncio
async def test_request_client_connection_error(api):
    """Test the _request function for an invalid client."""
    api._host = "http://0.0.0.0:1"

    with pytest.raises(ClientConnectionError):
        await api._request("/test")


@pytest.mark.asyncio
async def test_request_invalid_credentials(api):
    """Test the _request function for invalid credentials."""
    with aioresponses() as m:
        m.get(f"{api._host}/fhapi/v1/test", status=401)

        with pytest.raises(InvalidCredentialsException):
            await api._request("/test")


@pytest.mark.asyncio
async def test_request_forbidden(api):
    """Test the _request function for forbidden credentials."""
    with aioresponses() as m:
        m.get(f"{api._host}/fhapi/v1/test", status=403)

        with pytest.raises(ForbiddenAuthException):
            await api._request("/test")


@pytest.mark.asyncio
async def test_request_connection_timeout(api):
    """Test the _request function for connection timeout."""
    with aioresponses() as m:
        m.get(f"{api._host}/fhapi/v1/test", status=502)

        with pytest.raises(ConnectionTimeoutException):
            await api._request("/test")


@pytest.mark.asyncio
async def test_request_invalid_api_response(api):
    """Test the _request function for invalid api response."""
    with aioresponses() as m:
        m.get(f"{api._host}/fhapi/v1/test", status=500)

        with pytest.raises(InvalidApiResponseException):
            await api._request("/test")
