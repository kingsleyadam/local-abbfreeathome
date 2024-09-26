"""Test code to test all FreeAtHome class."""

from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import aiohttp
from aioresponses import aioresponses
import pytest

from abbfreeathome.api import FreeAtHomeApi
from abbfreeathome.exceptions import (
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


@pytest.mark.asyncio
async def test_aexit(api):
    """Test the __aexit__ function."""
    with patch.object(api, "ws_close", new_callable=AsyncMock) as mock_ws_close:
        await api.__aexit__()
        mock_ws_close.assert_called_once()


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
async def test_get_user(api):
    """Test the get_user function."""
    with patch.object(api, "get_settings", return_value=Mock()) as mock_get_settings:
        mock_get_settings.return_value = {"users": [{"name": "test_user"}]}
        user = await api.get_user("test_user")
        assert user == {"name": "test_user"}

        with pytest.raises(UserNotFoundException):
            await api.get_user("not_a_real_user")


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
        patch.object(
            FreeAtHomeApi, "_ws_session", new_callable=PropertyMock
        ) as mock_ws_session,
    ):
        mock_ws_session.return_value = AsyncMock()
        with patch.object(
            api._ws_session, "close", new_callable=AsyncMock
        ) as mock_close:
            await api.ws_close()
            mock_ws_disconnect.assert_called_once()
            mock_close.assert_called_once()


@pytest.mark.asyncio
async def test_ws_close_no_session(api):
    """Test the ws_close function with no session."""
    with (
        patch.object(
            FreeAtHomeApi, "ws_disconnect", new_callable=AsyncMock
        ) as mock_ws_disconnect,
        patch.object(
            FreeAtHomeApi, "_ws_session", new_callable=PropertyMock
        ) as mock_ws_session,
    ):
        mock_ws_session.return_value = None
        await api.ws_close()
        mock_ws_disconnect.assert_called_once()
        # Ensure no exception is raised and no call to close is made
        assert True


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
async def test_get_settings_success(api):
    """Test the get_settings function."""
    with aioresponses() as m:
        m.get(f"{api._host}/settings.json", payload={"key": "value"}, status=200)

        response = await api.get_settings()

        assert response == {"key": "value"}


@pytest.mark.asyncio
async def test_get_settings_invalid_host(api):
    """Test the get_settings function for invalid host."""
    api._host = "192.168.1.1"

    with pytest.raises(InvalidHostException):
        await api.get_settings()


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
