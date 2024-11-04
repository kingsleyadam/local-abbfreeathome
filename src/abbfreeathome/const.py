"""Constants for the FreeAtHome package."""

from .bin.function import Function
from .devices.base import Base
from .devices.brightness_sensor import BrightnessSensor
from .devices.carbon_monoxide_sensor import CarbonMonoxideSensor
from .devices.cover_actuator import (
    AtticWindowActuator,
    AwningActuator,
    BlindActuator,
    ShutterActuator,
)
from .devices.des_door_ringing_sensor import DesDoorRingingSensor
from .devices.dimming_actuator import DimmingActuator
from .devices.movement_detector import MovementDetector
from .devices.rain_sensor import RainSensor
from .devices.room_temperature_controller import RoomTemperatureController
from .devices.smoke_detector import SmokeDetector
from .devices.switch_actuator import SwitchActuator
from .devices.switch_sensor import SwitchSensor
from .devices.temperature_sensor import TemperatureSensor
from .devices.trigger import Trigger
from .devices.wind_sensor import WindSensor
from .devices.window_door_sensor import WindowDoorSensor

FUNCTION_DEVICE_MAPPING: dict[Function, Base] = {
    Function.FID_ATTIC_WINDOW_ACTUATOR: AtticWindowActuator,
    Function.FID_AWNING_ACTUATOR: AwningActuator,
    Function.FID_BLIND_ACTUATOR: BlindActuator,
    Function.FID_BRIGHTNESS_SENSOR: BrightnessSensor,
    Function.FID_CARBON_MONOXIDE_SENSOR: CarbonMonoxideSensor,
    Function.FID_DES_DOOR_RINGING_SENSOR: DesDoorRingingSensor,
    Function.FID_DIMMING_ACTUATOR: DimmingActuator,
    Function.FID_MOVEMENT_DETECTOR: MovementDetector,
    Function.FID_RAIN_SENSOR: RainSensor,
    Function.FID_ROOM_TEMPERATURE_CONTROLLER_MASTER_WITHOUT_FAN: (
        RoomTemperatureController
    ),
    Function.FID_SHUTTER_ACTUATOR: ShutterActuator,
    Function.FID_SMOKE_DETECTOR: SmokeDetector,
    Function.FID_SWITCH_ACTUATOR: SwitchActuator,
    Function.FID_SWITCH_SENSOR: SwitchSensor,
    Function.FID_SWITCH_SENSOR_PUSHBUTTON_TYPE0: SwitchSensor,
    Function.FID_SWITCH_SENSOR_PUSHBUTTON_TYPE1: SwitchSensor,
    Function.FID_SWITCH_SENSOR_PUSHBUTTON_TYPE2: SwitchSensor,
    Function.FID_SWITCH_SENSOR_PUSHBUTTON_TYPE3: SwitchSensor,
    Function.FID_SWITCH_SENSOR_ROCKER_TYPE0: SwitchSensor,
    Function.FID_SWITCH_SENSOR_ROCKER_TYPE1: SwitchSensor,
    Function.FID_SWITCH_SENSOR_ROCKER_TYPE2: SwitchSensor,
    Function.FID_TEMPERATURE_SENSOR: TemperatureSensor,
    Function.FID_TRIGGER: Trigger,
    Function.FID_WIND_SENSOR: WindSensor,
    Function.FID_WINDOW_DOOR_POSITION_SENSOR: WindowDoorSensor,
    Function.FID_WINDOW_DOOR_SENSOR: WindowDoorSensor,
}
