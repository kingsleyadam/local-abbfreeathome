"""Constants for the FreeAtHome package."""

from .bin.function import Function
from .devices.base import Base
from .devices.blind_sensor import BlindSensor
from .devices.brightness_sensor import BrightnessSensor
from .devices.carbon_monoxide_sensor import CarbonMonoxideSensor
from .devices.cover_actuator import (
    AtticWindowActuator,
    AwningActuator,
    BlindActuator,
    ShutterActuator,
)
from .devices.des_door_opener_actuator import DesDoorOpenerActuator
from .devices.des_door_ringing_sensor import DesDoorRingingSensor
from .devices.dimming_actuator import ColorTemperatureActuator, DimmingActuator
from .devices.force_on_off_sensor import ForceOnOffSensor
from .devices.heating_actuator import HeatingActuator
from .devices.movement_detector import MovementDetector
from .devices.rain_sensor import RainSensor
from .devices.room_temperature_controller import RoomTemperatureController
from .devices.smoke_detector import SmokeDetector
from .devices.switch_actuator import SwitchActuator
from .devices.switch_sensor import DimmingSensor, SwitchSensor
from .devices.temperature_sensor import TemperatureSensor
from .devices.trigger import Trigger
from .devices.virtual.virtual_brightness_sensor import VirtualBrightnessSensor
from .devices.virtual.virtual_energy_battery import VirtualEnergyBattery
from .devices.virtual.virtual_energy_inverter import VirtualEnergyInverter
from .devices.virtual.virtual_energy_two_way_meter import VirtualEnergyTwoWayMeter
from .devices.virtual.virtual_rain_sensor import VirtualRainSensor
from .devices.virtual.virtual_switch_actuator import VirtualSwitchActuator
from .devices.virtual.virtual_temperature_sensor import VirtualTemperatureSensor
from .devices.virtual.virtual_wind_sensor import VirtualWindSensor
from .devices.virtual.virtual_window_door_sensor import VirtualWindowDoorSensor
from .devices.wind_sensor import WindSensor
from .devices.window_door_sensor import WindowDoorSensor

FUNCTION_DEVICE_MAPPING: dict[Function, Base] = {
    Function.FID_ATTIC_WINDOW_ACTUATOR: AtticWindowActuator,
    Function.FID_AWNING_ACTUATOR: AwningActuator,
    Function.FID_BLIND_ACTUATOR: BlindActuator,
    Function.FID_BLINDS_ACTUATOR_TYPE0: ShutterActuator,
    Function.FID_BLINDS_ACTUATOR_TYPE1: BlindActuator,
    Function.FID_BLINDS_ACTUATOR_TYPE2: BlindActuator,
    Function.FID_BLINDS_ACTUATOR_TYPE3: BlindActuator,
    Function.FID_BLINDS_ACTUATOR_TYPE5: BlindActuator,
    Function.FID_BLINDS_ACTUATOR_TYPE8: BlindActuator,
    Function.FID_BLIND_SENSOR: BlindSensor,
    Function.FID_BLIND_SENSOR_ROCKER_TYPE0: BlindSensor,
    Function.FID_BLIND_SENSOR_ROCKER_TYPE1: BlindSensor,
    Function.FID_BLIND_SENSOR_ROCKER_TYPE2: BlindSensor,
    Function.FID_BLIND_SENSOR_ROCKER_TYPE7: BlindSensor,
    Function.FID_BLIND_SENSOR_PUSHBUTTON_TYPE0: BlindSensor,
    Function.FID_BLIND_SENSOR_PUSHBUTTON_TYPE1: BlindSensor,
    Function.FID_BLIND_SENSOR_PUSHBUTTON_TYPE2: BlindSensor,
    Function.FID_BLIND_SENSOR_PUSHBUTTON_TYPE3: BlindSensor,
    Function.FID_BLIND_SENSOR_PUSHBUTTON_TYPE7: BlindSensor,
    Function.FID_BRIGHTNESS_SENSOR: BrightnessSensor,
    Function.FID_CARBON_MONOXIDE_SENSOR: CarbonMonoxideSensor,
    Function.FID_COLORTEMPERATURE_ACTUATOR: ColorTemperatureActuator,
    Function.FID_DES_DOOR_OPENER_ACTUATOR: DesDoorOpenerActuator,
    Function.FID_DES_DOOR_RINGING_SENSOR: DesDoorRingingSensor,
    Function.FID_DES_LEVEL_CALL_SENSOR: DesDoorRingingSensor,
    Function.FID_DIMMING_ACTUATOR: DimmingActuator,
    Function.FID_DIMMING_ACTUATOR_TYPE0: DimmingActuator,
    Function.FID_DIMMING_ACTUATOR_TYPE1: DimmingActuator,
    Function.FID_DIMMING_ACTUATOR_TYPE2: DimmingActuator,
    Function.FID_DIMMING_ACTUATOR_TYPE8: DimmingActuator,
    Function.FID_DIMMING_ACTUATOR_TYPE9: DimmingActuator,
    Function.FID_DIMMING_SENSOR: DimmingSensor,
    Function.FID_DIMMING_SENSOR_PUSHBUTTON_TYPE0: DimmingSensor,
    Function.FID_DIMMING_SENSOR_PUSHBUTTON_TYPE1: DimmingSensor,
    Function.FID_DIMMING_SENSOR_PUSHBUTTON_TYPE2: DimmingSensor,
    Function.FID_DIMMING_SENSOR_PUSHBUTTON_TYPE3: DimmingSensor,
    Function.FID_DIMMING_SENSOR_PUSHBUTTON_TYPE4: DimmingSensor,
    Function.FID_DIMMING_SENSOR_PUSHBUTTON_TYPE5: DimmingSensor,
    Function.FID_DIMMING_SENSOR_PUSHBUTTON_TYPE6: DimmingSensor,
    Function.FID_DIMMING_SENSOR_PUSHBUTTON_TYPE7: DimmingSensor,
    Function.FID_DIMMING_SENSOR_ROCKER_TYPE0: DimmingSensor,
    Function.FID_DIMMING_SENSOR_ROCKER_TYPE1: DimmingSensor,
    Function.FID_DIMMING_SENSOR_ROCKER_TYPE2: DimmingSensor,
    Function.FID_DIMMING_SENSOR_ROCKER_TYPE3: DimmingSensor,
    Function.FID_DIMMING_SENSOR_ROCKER_TYPE4: DimmingSensor,
    Function.FID_DIMMING_SENSOR_ROCKER_TYPE5: DimmingSensor,
    Function.FID_DIMMING_SENSOR_ROCKER_TYPE6: DimmingSensor,
    Function.FID_DIMMING_SENSOR_ROCKER_TYPE7: DimmingSensor,
    Function.FID_FORCE_ON_OFF_SENSOR: ForceOnOffSensor,
    Function.FID_HEATING_ACTUATOR: HeatingActuator,
    Function.FID_MOVEMENT_DETECTOR: MovementDetector,
    Function.FID_MOVEMENT_DETECTOR_TYPE7: MovementDetector,
    Function.FID_RAIN_SENSOR: RainSensor,
    Function.FID_ROOM_TEMPERATURE_CONTROLLER_MASTER_WITHOUT_FAN: (
        RoomTemperatureController
    ),
    Function.FID_ROOM_TEMPERATURE_CONTROLLER_MASTER_WITHOUT_FAN_TYPE1: (
        RoomTemperatureController
    ),
    Function.FID_PANEL_ROOM_TEMPERATURE_CONTROLLER_MASTER_WITHOUT_FAN: (
        RoomTemperatureController
    ),
    Function.FID_SHUTTER_ACTUATOR: ShutterActuator,
    Function.FID_SMOKE_DETECTOR: SmokeDetector,
    Function.FID_SWITCH_ACTUATOR: SwitchActuator,
    Function.FID_E_CONTACT_SWITCH_ACTUATOR_TYPE0: SwitchActuator,
    Function.FID_E_CONTACT_SWITCH_ACTUATOR_TYPE1: SwitchActuator,
    Function.FID_E_CONTACT_SWITCH_ACTUATOR_TYPE2: SwitchActuator,
    Function.FID_SWITCH_ACTUATOR_TYPE1: SwitchActuator,
    Function.FID_SWITCH_SENSOR: SwitchSensor,
    Function.FID_SWITCH_SENSOR_PUSHBUTTON_TYPE0: SwitchSensor,
    Function.FID_SWITCH_SENSOR_PUSHBUTTON_TYPE1: SwitchSensor,
    Function.FID_SWITCH_SENSOR_PUSHBUTTON_TYPE2: SwitchSensor,
    Function.FID_SWITCH_SENSOR_PUSHBUTTON_TYPE3: SwitchSensor,
    Function.FID_SWITCH_SENSOR_PUSHBUTTON_TYPE4: SwitchSensor,
    Function.FID_SWITCH_SENSOR_PUSHBUTTON_TYPE7: SwitchSensor,
    Function.FID_SWITCH_SENSOR_ROCKER_TYPE0: SwitchSensor,
    Function.FID_SWITCH_SENSOR_ROCKER_TYPE1: SwitchSensor,
    Function.FID_SWITCH_SENSOR_ROCKER_TYPE2: SwitchSensor,
    Function.FID_TEMPERATURE_SENSOR: TemperatureSensor,
    Function.FID_TRIGGER: Trigger,
    Function.FID_WIND_SENSOR: WindSensor,
    Function.FID_WINDOW_DOOR_POSITION_SENSOR: WindowDoorSensor,
    Function.FID_WINDOW_DOOR_SENSOR: WindowDoorSensor,
}

FUNCTION_VIRTUAL_DEVICE_MAPPING: dict[Function, Base] = {
    Function.FID_BRIGHTNESS_SENSOR: VirtualBrightnessSensor,
    Function.FID_ENERGY_BATTERY: VirtualEnergyBattery,
    Function.FID_ENERGY_INVERTER: VirtualEnergyInverter,
    Function.FID_ENERGY_TWO_WAY_METER: VirtualEnergyTwoWayMeter,
    Function.FID_RAIN_SENSOR: VirtualRainSensor,
    Function.FID_SWITCH_ACTUATOR: VirtualSwitchActuator,
    Function.FID_TEMPERATURE_SENSOR: VirtualTemperatureSensor,
    Function.FID_WIND_SENSOR: VirtualWindSensor,
    Function.FID_WINDOW_DOOR_SENSOR: VirtualWindowDoorSensor,
}
