"""Constants for the FreeAtHome package."""

from .bin.function import Function
from .devices.base import Base
from .devices.carbon_monoxide_sensor import CarbonMonoxideSensor
from .devices.des_door_ringing_sensor import DesDoorRingingSensor
from .devices.dimming_actuator import DimmingActuator
from .devices.movement_detector import MovementDetector
from .devices.smoke_detector import SmokeDetector
from .devices.switch_actuator import SwitchActuator
from .devices.switch_sensor import SwitchSensor
from .devices.trigger import Trigger
from .devices.window_door_sensor import WindowDoorSensor

FUNCTION_DEVICE_MAPPING: dict[Function, Base] = {
    Function.FID_CARBON_MONOXIDE_SENSOR: CarbonMonoxideSensor,
    Function.FID_DES_DOOR_RINGING_SENSOR: DesDoorRingingSensor,
    Function.FID_DIMMING_ACTUATOR: DimmingActuator,
    Function.FID_MOVEMENT_DETECTOR: MovementDetector,
    Function.FID_SMOKE_DETECTOR: SmokeDetector,
    Function.FID_SWITCH_ACTUATOR: SwitchActuator,
    Function.FID_SWITCH_SENSOR: SwitchSensor,
    Function.FID_TRIGGER: Trigger,
    Function.FID_WINDOW_DOOR_POSITION_SENSOR: WindowDoorSensor,
    Function.FID_WINDOW_DOOR_SENSOR: WindowDoorSensor,
}
