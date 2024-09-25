"""Exceptions used within the Free@Home library."""


class FreeAtHomeException(Exception):
    """A base class for Free@Home exceptions."""


class ConnectionTimeoutException(FreeAtHomeException):
    """Raise an exception if the connection times out."""

    def __init__(self, host) -> None:
        """Initialze the ConnectionTimeoutException class."""
        self.message = f"Connection timeout to host: {host}"
        super().__init__(self.message)


class ForbiddenAuthException(FreeAtHomeException):
    """Raise an exception if the connection returns a forbidden code."""

    def __init__(self, path) -> None:
        """Initialze the ForbiddenAuthException class."""
        self.message = f"Request returned a forbidden (401) error message: {path}"
        super().__init__(self.message)


class InvalidCredentialsException(FreeAtHomeException):
    """Raise an exception for invalid credentials."""

    def __init__(self, username: str) -> None:
        """Initialze the InvalidCredentialsException class."""
        self.message = f"Invalid credentials for user: {username}"
        super().__init__(self.message)


class InvalidHostException(FreeAtHomeException):
    """Raise an exception for an invalid URL format."""

    def __init__(self, url: str) -> None:
        """Initialze the InvalidHostException class."""
        self.message = (
            f"Invalid Host endpoint, ensure url includes schema (e.g. http://): {url}"
        )
        super().__init__(self.message)


class InvalidApiResponseException(FreeAtHomeException):
    """Raise an exception for an invalid api response code."""

    def __init__(self, status_code: int) -> None:
        """Initialze the InvalidApiResponseException class."""
        self.message = f"Invalid api response, status code: {status_code}"
        super().__init__(self.message)


class InvalidDeviceChannelPairingId(FreeAtHomeException):
    """Raise an exception for an invalid pairing id."""

    def __init__(self, device_id: str, channel_id: str, pairing_id: int) -> None:
        """Initialze the InvalidDeviceChannelPairingId class."""
        self.message = (
            f"Could not find paring id for "
            f"device: {device_id}; channel: {channel_id}; pairing id: {pairing_id}"
        )
        super().__init__(self.message)


class UserNotFoundException(FreeAtHomeException):
    """Raise an exception if a user is not found."""

    def __init__(self, username: str):
        """Initialize UserNotFoundException class."""
        self.message = f"User not found; {username}."
        super().__init__(self.message)


class SetDatapointFailureException(FreeAtHomeException):
    """Raise an exception when setting a datapoint fails."""

    def __init__(self, device_id: str, channel_id: str, datapoint: str, value: str):
        """Initialize the SetDatapointFailureException class."""
        self.message = (
            f"Failed to set datapoint; device_id: "
            f"{device_id}; "
            f"channel_id: {channel_id}; "
            f"datapoint: {datapoint}; "
            f"value: {value}"
        )
        super().__init__(self.message)
