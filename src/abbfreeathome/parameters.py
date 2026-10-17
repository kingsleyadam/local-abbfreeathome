"""Shared parameter handling for Free@Home devices and channels."""

from collections.abc import Callable
import logging
from typing import Any

from .bin.parameter import Parameter

_LOGGER = logging.getLogger(__name__)


class ParametersMixin:
    """Expose parameters and notify callbacks when their values change."""

    _parameters: dict[str, Any]

    @property
    def parameters(self) -> dict[str, Any]:
        """Return the parameters, keyed by id (e.g. ``par0002``)."""
        return self._parameters

    def get_parameter(self, parameter_id: str | int | Parameter) -> Any | None:
        """Get a parameter value by id (``"par0002"`` or the int ``2``)."""
        return self._parameters.get(_normalize_parameter_id(parameter_id))

    def get_parameter_name(self, parameter_id: str | int | Parameter) -> str | None:
        """
        Get the Free@Home name of a parameter (e.g. ``PID_LED_OPERATION_MODE``).

        Returns None when the id is not a known parameter.
        """
        try:
            return Parameter(_parameter_number(parameter_id)).name
        except ValueError:
            return None

    def update_parameter(self, parameter_id: str | int | Parameter, value: Any) -> bool:
        """
        Update a parameter value, notifying callbacks if it changed.

        Returns True when the value changed.
        """
        _parameter_id = _normalize_parameter_id(parameter_id)
        if self._parameters.get(_parameter_id) == value:
            return False

        self._parameters[_parameter_id] = value
        _LOGGER.info("%s parameter %s updated: %s", self, _parameter_id, value)

        for _filter_id, _callback in list(self._get_parameter_callbacks()):
            if _filter_id is None or _filter_id == _parameter_id:
                _callback()
        return True

    def register_parameter_callback(
        self,
        callback: Callable[[], None],
        parameter_id: str | int | Parameter | None = None,
    ) -> None:
        """Register a callback for parameter changes (optionally one parameter)."""
        _filter = (
            None if parameter_id is None else _normalize_parameter_id(parameter_id)
        )
        self._get_parameter_callbacks().add((_filter, callback))

    def remove_parameter_callback(
        self,
        callback: Callable[[], None],
        parameter_id: str | int | Parameter | None = None,
    ) -> None:
        """Remove a previously registered parameter callback."""
        _filter = (
            None if parameter_id is None else _normalize_parameter_id(parameter_id)
        )
        self._get_parameter_callbacks().discard((_filter, callback))

    def _get_parameter_callbacks(self) -> set:
        if not hasattr(self, "_parameter_callbacks"):
            self._parameter_callbacks: set = set()
        return self._parameter_callbacks


def _parameter_number(parameter_id: str | int | Parameter) -> int:
    """Convert ``Parameter.X``/``2``/``"par0002"`` to its integer id."""
    if isinstance(parameter_id, Parameter):
        return parameter_id.value
    if isinstance(parameter_id, int):
        return parameter_id
    return int(parameter_id.lower().removeprefix("par"), 16)


def _normalize_parameter_id(parameter_id: str | int | Parameter) -> str:
    """Normalize ``Parameter.X``/``2``/``"par0002"`` to the ``par0002`` form."""
    if isinstance(parameter_id, str):
        return parameter_id.lower()
    return f"par{_parameter_number(parameter_id):04x}"
