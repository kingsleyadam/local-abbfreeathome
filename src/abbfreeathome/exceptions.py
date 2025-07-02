"""Exceptions used within the Free@Home library."""


class FreeAtHomeException(Exception):
    """A base class for Free@Home exceptions."""


class ClientConnectionError(FreeAtHomeException):
    """Raise an exception for client connector error."""

    def __init__(self, url: str) -> None:
        """Initialze the ClientConnectorError class."""
        self.message = f"Cannot connect to host {url}"
        super().__init__(self.message)


class ConnectionTimeoutException(FreeAtHomeException):
    """Raise an exception if the connection times out."""

    def __init__(self, host) -> None:
        """Initialze the ConnectionTimeoutException class."""
        self.message = f"Connection timeout to host: {host}"
        super().__init__(self.message)


class ForbiddenAuthException(FreeAtHomeException):
    """Raise an exception if the connection returns a forbidden code."""

    def __init__(self, path, status_code) -> None:
        """Initialze the ForbiddenAuthException class."""
        self.message = (
            "Request returned a forbidden error message "
            f"(status code: {status_code}): "
            f"{path}"
        )
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


class InvalidDeviceChannelPairing(FreeAtHomeException):
    """Raise an exception for an invalid pairing id."""

    def __init__(self, device_serial: str, channel_id: str, pairing_value: int) -> None:
        """Initialze the InvalidDeviceChannelPairing class."""
        self.message = (
            f"Could not find paring id for "
            f"device: {device_serial}; "
            f"channel: {channel_id}; "
            f"pairing id: {pairing_value}"
        )
        super().__init__(self.message)


class InvalidDeviceChannelParameter(FreeAtHomeException):
    """Raise an exception for an invalid parameter id."""

    def __init__(
        self, device_serial: str, channel_id: str, parameter_value: int
    ) -> None:
        """Initialze the InvalidDeviceChannelParameter class."""
        self.message = (
            f"Could not find parameter id for "
            f"device: {device_serial}; channel: {channel_id}; "
            f"parameter id: {parameter_value}"
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

    def __init__(self, device_serial: str, channel_id: str, datapoint: str, value: str):
        """Initialize the SetDatapointFailureException class."""
        self.message = (
            f"Failed to set datapoint; device_serial: "
            f"{device_serial}; "
            f"channel_id: {channel_id}; "
            f"datapoint: {datapoint}; "
            f"value: {value}"
        )
        super().__init__(self.message)


class UnknownCallbackAttributeException(FreeAtHomeException):
    """Raise an exception when an unknown callback-attribute should be registered."""

    def __init__(self, unknown_attribute: str, known_attributes: str):
        """Initialize the UnknownCallbackAttributeException class."""
        self.message = (
            f"Tried to register the callback-atrribute: "
            f"{unknown_attribute}"
            f", but only the callback-attributes '"
            f"{known_attributes}"
            f"' are known."
        )
        super().__init__(self.message)


class BadRequestException(FreeAtHomeException):
    """Raise an exception for bad requests."""

    def __init__(self, data: str) -> None:
        """Initialze the BadRequestException class."""
        self.message = f"Bad Request with data: {data}"
        super().__init__(self.message)
