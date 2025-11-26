"""Free@Home HeatingActuator Class - Backward Compatibility."""

# Added for backwards compatibility: import from new location
from .valve_actuator import HeatingActuator

__all__ = ["HeatingActuator"]
