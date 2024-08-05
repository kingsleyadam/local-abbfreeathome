class FreeAtHomeException(Exception):
    """A base class for Free@Home exceptions."""


class InvalidCredentialsException(FreeAtHomeException):
    """Raise an exception for invalid credentials."""

class UserNotFoundException(FreeAtHomeException):
    """Raise an exception if a user is not found."""


class SetDatapointFailureException(FreeAtHomeException):
    """Raise an exception when setting a datapoint fails."""
