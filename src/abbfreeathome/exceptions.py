"""Exceptions used within the Free@Home library."""


class FreeAtHomeException(Exception):
    """A base class for Free@Home exceptions."""


class InvalidCredentialsException(FreeAtHomeException):
    """Raise an exception for invalid credentials."""

    def __init__(self, username: str) -> None:
        """Initialze the InvalidCredentialsException class."""
        self.message = f"Invalid credentials for user: {username}"
        super().__init__(self.message)


class InvalidURLSchemaException(FreeAtHomeException):
    """Raise an excpetion for an invalid URL format."""

    def __init__(self, url: str) -> None:
        """Initialze the InvalidCredentialsException class."""
        self.message = f"Invalid URL, ensure url includes schema (e.g. http://): {url}"
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
