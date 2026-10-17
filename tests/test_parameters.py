"""Test the parameters mixin."""

from unittest.mock import MagicMock

from src.abbfreeathome.bin.parameter import Parameter
from src.abbfreeathome.parameters import ParametersMixin


class _Holder(ParametersMixin):
    def __init__(self) -> None:
        self._parameters = {"par0015": "360"}


def test_get_parameter_accepts_str_int_and_enum():
    """Parameters can be read by id string, int or Parameter enum."""
    holder = _Holder()
    assert holder.get_parameter("PAR0015") == "360"
    assert holder.get_parameter(0x15) == "360"
    assert holder.get_parameter(Parameter.PID_AUTONOMOUS_SWITCH_OFF_TIME_DURATION) == (
        "360"
    )
    assert holder.get_parameter("par9999") is None


def test_get_parameter_name():
    """Known ids resolve to the enum name, unknown ids to None."""
    holder = _Holder()
    assert holder.get_parameter_name("par0015") == (
        "PID_AUTONOMOUS_SWITCH_OFF_TIME_DURATION"
    )
    assert holder.get_parameter_name(0x7) == "PID_LED_OPERATION_MODE"
    assert holder.get_parameter_name(Parameter.PID_LED_OPERATION_MODE) == (
        "PID_LED_OPERATION_MODE"
    )
    assert holder.get_parameter_name("par7fff") is None
    assert holder.get_parameter_name("not-a-parameter") is None


def test_callback_filter_by_enum():
    """Callbacks can be filtered using the Parameter enum."""
    holder = _Holder()
    callback = MagicMock()
    holder.register_parameter_callback(
        callback, parameter_id=Parameter.PID_AUTONOMOUS_SWITCH_OFF_TIME_DURATION
    )

    assert holder.update_parameter("par0015", "360") is False
    assert holder.update_parameter(0x15, "400") is True
    callback.assert_called_once()
