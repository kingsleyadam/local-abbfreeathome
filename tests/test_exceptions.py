"""Test code to test all abb exceptions."""

import pytest

from src.abbfreeathome.exceptions import (
    ConnectionTimeoutException,
    ForbiddenAuthException,
    InvalidApiResponseException,
    InvalidCredentialsException,
    InvalidDeviceChannelPairing,
    InvalidHostException,
    SetDatapointFailureException,
    UserNotFoundException,
)


def test_connection_timeout_exception():
    """Test connection timeout exception."""
    with pytest.raises(ConnectionTimeoutException) as excinfo:
        raise ConnectionTimeoutException("192.168.1.1")
    assert str(excinfo.value) == "Connection timeout to host: 192.168.1.1"


def test_forbidden_auth_exception():
    """Test forbidden auth exception."""
    with pytest.raises(ForbiddenAuthException) as excinfo:
        raise ForbiddenAuthException("/api/path")
    assert (
        str(excinfo.value)
        == "Request returned a forbidden (401) error message: /api/path"
    )


def test_invalid_credentials_exception():
    """Test invalid credentials exception."""
    with pytest.raises(InvalidCredentialsException) as excinfo:
        raise InvalidCredentialsException("user123")
    assert str(excinfo.value) == "Invalid credentials for user: user123"


def test_invalid_host_exception():
    """Test invalid host exception."""
    with pytest.raises(InvalidHostException) as excinfo:
        raise InvalidHostException("example.com")
    assert str(excinfo.value) == (
        "Invalid Host endpoint, ensure url includes schema (e.g. http://): example.com"
    )


def test_invalid_api_response_exception():
    """Test invalid api response exception."""
    with pytest.raises(InvalidApiResponseException) as excinfo:
        raise InvalidApiResponseException(404)
    assert str(excinfo.value) == "Invalid api response, status code: 404"


def test_invalid_device_channel_pairing():
    """Test invalid device channel exception."""
    with pytest.raises(InvalidDeviceChannelPairing) as excinfo:
        raise InvalidDeviceChannelPairing("device1", "channel1", 123)
    assert str(excinfo.value) == (
        "Could not find paring id for "
        "device: device1; channel: channel1; pairing id: 123"
    )


def test_user_not_found_exception():
    """Test user not found exception."""
    with pytest.raises(UserNotFoundException) as excinfo:
        raise UserNotFoundException("user123")
    assert str(excinfo.value) == "User not found; user123."


def test_set_datapoint_failure_exception():
    """Test set datapoint failure exception."""
    with pytest.raises(SetDatapointFailureException) as excinfo:
        raise SetDatapointFailureException(
            "device1", "channel1", "datapoint1", "value1"
        )
    assert str(excinfo.value) == (
        "Failed to set datapoint; "
        "device_id: device1; channel_id: channel1; datapoint: datapoint1; value: value1"
    )
