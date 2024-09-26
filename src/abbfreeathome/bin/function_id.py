"""
Defines the avaliable functions in the Free@Home System.

See: https://developer.eu.mybuildings.abb.com/fah_local/reference/functionids
"""

import enum


class FunctionID(enum.Enum):
    """An Enum class for all Free@Home Functions."""

    FID_SWITCH_SENSOR = "0"
    FID_DIMMING_SENSOR = "1"
    FID_SHUTTER_SENSOR = "2"
    FID_BLIND_SENSOR = "3"
    FID_STAIRCASE_LIGHT_SENSOR = "4"
    FID_FORCE_ON_OFF_SENSOR = "5"
    FID_SCENE_SENSOR = "6"
    FID_SWITCH_ACTUATOR = "7"
    FID_STAIRCASE_LIGHT_ACTUATOR = "8"
    FID_SHUTTER_ACTUATOR = "9"
    FID_ROOM_TEMPERATURE_CONTROLLER_MASTER_WITH_FAN = "a"
    FID_ROOM_TEMPERATURE_CONTROLLER_SLAVE = "b"
    FID_WIND_ALARM_SENSOR = "c"
    FID_FROST_ALARM_SENSOR = "d"
    FID_RAIN_ALARM_SENSOR = "e"
    FID_WINDOW_DOOR_SENSOR = "f"
    FID_NOTIFICATION_SENSOR = "10"
    FID_MOVEMENT_DETECTOR = "11"
    FID_DIMMING_ACTUATOR = "12"
    FID_NOTIFICATION_CENTER = "13"
    FID_RADIATOR_ACTUATOR = "14"
    FID_UNDERFLOOR_HEATING = "15"
    FID_FAN_COIL = "16"
    FID_TWO_LEVEL_CONTROLLER = "17"
    FID_PUSH_BUTTON_SENSOR = "18"
    FID_RING_INDICATION_SENSOR = "19"
    FID_DES_DOOR_OPENER_ACTUATOR = "1a"
    FID_PROXY = "1b"
    FID_FAN_COIL_SENSOR = "1c"
    FID_DES_LEVEL_CALL_ACTUATOR = "1d"
    FID_DES_LEVEL_CALL_SENSOR = "1e"
    FID_DES_DOOR_RINGING_SENSOR = "1f"
    FID_DES_AUTOMATIC_DOOR_OPENER_ACTUATOR = "20"
    FID_DES_LIGHT_SWITCH_ACTUATOR = "21"
    FID_DES_UNKNOWN_HVAC_ACTUATOR = "22"
    FID_ROOM_TEMPERATURE_CONTROLLER_MASTER_WITHOUT_FAN = "23"
    FID_COOLING_ACTUATOR = "24"
    FID_DAY_NIGHT_SENSOR = "25"
    FID_DATE_AND_TIME = "26"
    FID_HEATING_ACTUATOR = "27"
    FID_FORCE_UP_DOWN_SENSOR = "28"
    FID_HEATING_COOLING_ACTUATOR = "29"
    FID_HEATING_COOLING_SENSOR = "2a"
    FID_DES_DEVICE_SETTINGS = "2b"
    FID_SACE_BLIND_ACTUATOR = "2c"
    FID_RGB_SENSOR = "2d"
    FID_RGB_W_ACTUATOR = "2e"
    FID_RGB_ACTUATOR = "2f"
    FID_PANEL_SWITCH_SENSOR = "30"
    FID_PANEL_DIMMING_SENSOR = "31"
    FID_PANEL_SHUTTER_SENSOR = "32"
    FID_PANEL_BLIND_SENSOR = "33"
    FID_PANEL_STAIRCASE_LIGHT_SENSOR = "34"
    FID_PANEL_FORCE_ON_OFF_SENSOR = "35"
    FID_PANEL_FORCE_UP_DOWN_SENSOR = "36"
    FID_PANEL_SCENE_SENSOR = "37"
    FID_PANEL_ROOM_TEMPERATURE_CONTROLLER_SLAVE = "38"
    FID_PANEL_FAN_COIL_SENSOR = "39"
    FID_PANEL_RGB_CT_SENSOR = "3a"
    FID_PANEL_RGB_SENSOR = "3b"
    FID_PANEL_CT_SENSOR = "3c"
    FID_ADDITIONAL_HEATING_ACTUATOR = "3d"
    FID_RADIATOR_ACTUATOR_MASTER = "3e"
    FID_RADIATOR_ACTUATOR_SLAVE = "3f"
    FID_COLORTEMPERATURE_ACTUATOR = "40"
    FID_BRIGHTNESS_SENSOR = "41"
    FID_RAIN_SENSOR = "42"
    FID_TEMPERATURE_SENSOR = "43"
    FID_WIND_SENSOR = "44"
    FID_TRIGGER = "45"
    FID_FCA_2_PIPE_HEATING = "47"
    FID_FCA_2_PIPE_COOLING = "48"
    FID_FCA_2_PIPE_HEATING_COOLING = "49"
    FID_FCA_4_PIPE_HEATING_AND_COOLING = "4a"
    FID_WINDOW_DOOR_ACTUATOR = "4b"
    DEPRECATED_004C = "4c"
    DEPRECATED_004D = "4d"
    FID_INVERTER_INFO = "4e"
    FID_METER_INFO = "4f"
    FID_BATTERY_INFO = "50"
    FID_PANEL_TIMER_PROGRAM_SWITCH_SENSOR = "51"
    DEPRECATED_0052 = "52"
    FID_SAFETY_SENSOR = "53"
    FID_CENTRAL_UNIT_ACTUATOR = "54"
    FID_DOMUSTECH_ZONE = "55"
    FID_CENTRAL_HEATING_ACTUATOR = "56"
    FID_CENTRAL_COOLING_ACTUATOR = "57"
    FID_LINK_ACTUATOR = "58"
    FID_HOUSE_KEEPING = "59"
    FID_MEDIA_PLAYER = "5a"
    FID_PANEL_ROOM_TEMPERATURE_CONTROLLER_SLAVE_FOR_BATTERY_DEVICE = "5b"
    FID_WELCOME_IP_MUTE_SENSOR = "5c"
    FID_WELCOME_IP_MUTE_ACTUATOR = "5d"
    FID_WELCOME_IP_DOOR_OPEN_SENSOR = "5e"
    FID_WELCOME_IP_SWITCH_SENSOR = "5f"
    FID_PANEL_MEDIA_PLAYER_SENSOR = "60"
    FID_BLIND_ACTUATOR = "61"
    FID_ATTIC_WINDOW_ACTUATOR = "62"
    FID_AWNING_ACTUATOR = "63"
    FID_WINDOW_DOOR_POSITION_SENSOR = "64"
    FID_WINDOW_DOOR_POSITION_ACTUATOR = "65"
    FID_MEDIA_PLAYBACK_CONTROL_SENSOR = "66"
    FID_MEDIA_VOLUME_SENSOR = "67"
    FID_DISHWASHER = "68"
    FID_LAUNDRY = "69"
    FID_DRYER = "6a"
    FID_OVEN = "6b"
    FID_FRIDGE = "6c"
    FID_FREEZER = "6d"
    FID_HOOD = "6e"
    FID_COFFEE_MACHINE = "6f"
    FID_FRIDGE_FREEZER = "70"
    FID_TIMER_PROGRAM_OR_ALERT_SWITCH_SENSOR = "71"
    FID_WELCOME_IP_BELL_INDICATOR_SENSOR = "72"
    FID_CEILING_FAN_ACTUATOR = "73"
    FID_CEILING_FAN_SENSOR = "74"
    FID_SPLIT_UNIT_GATEWAY = "75"
    FID_ZONE = "76"
    FID_24H_ZONE = "77"
    FID_EXTERNAL_IR_SENSOR_BX80 = "78"
    FID_EXTERNAL_IR_SENSOR_VXI = "79"
    FID_EXTERNAL_IR_SENSOR_MINI = "7a"
    FID_EXTERNAL_IR_SENSOR_HIGH_ALTITUDE = "7b"
    FID_EXTERNAL_IR_SENSOR_CURTAIN = "7c"
    FID_SMOKE_DETECTOR = "7d"
    FID_CARBON_MONOXIDE_SENSOR = "7e"
    FID_METHANE_DETECTOR = "7f"
    FID_GAS_SENSOR_LPG = "80"
    FID_FLOOD_DETECTION = "81"
    FID_DOMUS_CENTRAL_UNIT_NEXTGEN = "82"
    FID_THERMOSTAT = "83"
    FID_PANEL_DOMUS_ZONE_SENSOR = "84"
    FID_THERMOSTAT_SLAVE = "85"
    FID_DOMUS_SECURE_INTEGRATION = "86"
    FID_ADDITIONAL_COOLING_ACTUATOR = "87"
    FID_TWO_LEVEL_HEATING_ACTUATOR = "88"
    FID_TWO_LEVEL_COOLING_ACTUATOR = "89"
    FID_DOOR_LOCK_SENSOR = "8a"
    FID_DOOR_LOCK_ACTUATOR = "8b"
    FID_AC_ROUTING = "8c"
    FID_EXTERNAL_SIREN = "8d"
    FID_GLOBAL_ZONE = "8e"
    FID_VOLUME_UP_SENSOR = "8f"
    FID_VOLUME_DOWN_SENSOR = "90"
    FID_PLAY_PAUSE_SENSOR = "91"
    FID_NEXT_FAVORITE_SENSOR = "92"
    FID_NEXT_SONG_SENSOR = "93"
    FID_PREVIOUS_SONG_SENSOR = "94"
    FID_HOME_APPLIANCE_SENSOR = "95"
    FID_HEAT_SENSOR = "96"
    FID_ZONE_SWITCHING = "97"
    FID_SECURE_AT_HOME_FUNCTION = "98"
    FID_COMPLEX_CONFIGURATION = "99"
    FID_DOMUS_CENTRAL_UNIT_BASIC = "9a"
    FID_DOMUS_REPEATER = "9b"
    FID_DOMUS_SCENE_TRIGGER = "9c"
    FID_DOMUS_WINDOW_CONTACT = "9d"
    FID_DOMUS_MOVEMENT_DETECTOR = "9e"
    FID_DOMUS_CURTAIN_DETECTOR = "9f"
    FID_DOMUS_SMOKE_DETECTOR = "a0"
    FID_DOMUS_FLOOD_DETECTOR = "a1"
    FID_HOB = "a2"
    FID_PANEL_SUG_SENSOR = "a3"
    FID_TWO_LEVEL_HEATING_COOLING_ACTUATOR = "a4"
    FID_PANEL_THERMOSTAT_CONTROLLER_SLAVE = "a5"
    FID_WALLBOX = "a6"
    FID_PANEL_WALLBOX = "a7"
    FID_DOOR_LOCK_CONTROL = "a8"
    FID_DOOR_LOCK_SETTINGS = "a9"
    FID_VRV_GATEWAY = "aa"
    FID_DOMUS_PARAMETRABLE_BUTTON = "ab"
    FID_DOMUS_CENTRAL_UNIT_BASIC_25 = "ac"
    FID_DOMUS_CENTRAL_UNIT_NEXTGEN_25 = "ad"
    FID_PANEL_RGB_W_SENSOR = "ae"
    FID_INVERTER_METER_BATTERY = "af"
    FID_INVERTER_METER = "b0"
    FID_METER_BATTERY = "b1"
    FID_INVERTER_BATTERY = "b2"
    FID_DES_VIDEO_CAMERA_LINK = "b3"
    FID_FINGERPRINT_SENSOR = "b4"
    FID_FLOOD_ALARM_SENSOR = "b5"
    FID_DOMUS_PRE_PROGRAMMED_REMOTE = "b6"
    FID_HVAC = "b7"
    FID_TIMED_START_STOP_ACTUATOR = "b8"
    FID_VENTILATION = "b9"
    FID_CO_2 = "ba"
    FID_VOC = "bb"
    FID_TEMPERATURE_SENSOR_TYPE1 = "bc"
    FID_AIRQUALITY_SENSOR = "bd"
    FID_VACUUM_CLEANER = "be"
    FID_PANEL_ROOM_TEMPERATURE_CONTROLLER_SLAVE_1X1 = "bf"
    FID_SMOKE_DETECTOR_TYPE1 = "c0"
    FID_PANEL_ROOM_TEMPERATURE_CONTROLLER_MASTER_WITHOUT_FAN = "c1"
    FID_PANEL_ROOM_TEMPERATURE_CONTROLLER_MASTER_WITH_FAN = "c2"
    FID_DES_VIDEO_CAMERA_ACTUATOR = "c3"
    FID_ENERGY_ONE_WAY_METER = "c4"
    FID_ENERGY_TWO_WAY_METER = "c5"
    FID_ENERGY_INVERTER = "c6"
    FID_ENERGY_BATTERY = "c7"
    FID_WATER_METER = "c8"
    FID_GAS_METER = "c9"
    FID_CWA_ROOM_TEMPERATURE_CONTROLLER_UNDERFLOOR = "cf"
    FID_CWA_UNDERFLOOR_TEMPERATURE_CONTROLLER = "d0"
    FID_CWA_ROOM_TEMPERATURE_CONTROLLER_UNDERFLOOR_LIMITER = "d1"
    FID_CWA_ROOM_TEMPERATURE_CONTROLLER_HEATING_COOLING = "d2"
    FID_CWA_ROOM_TEMPERATURE_CONTROLLER_RADIATOR = "d3"
    FID_PANEL_LIGHT_SWITCH_SENSOR = "d4"
    FID_FLASHING_ACTUATOR = "d5"
    FID_PB_SWITCH_SENSOR = "d6"
    FID_PB_BLIND_SENSOR = "d7"
    FID_PB_STAIRCASE_LIGHT_SENSOR = "d8"
    FID_PB_SCENE_SENSOR = "d9"
    FID_DALI_DT0_ACTUATOR = "da"
    FID_DALI_DT8_CT_ACTUATOR = "db"
    FID_DALI_DT8_RGB_ACTUATOR = "dc"
    FID_COLORTEMPERATURE_ACTUATOR_TYPE8 = "de"
    FID_RGB_ACTUATOR_TYPE8 = "df"
    FID_RGB_W_ACTUATOR_TYPE8 = "e0"
    FID_CEILING_FAN_ACTUATOR_TYPE8 = "e1"
    FID_MEDIA_PLAYER_TYPE1 = "e2"
    FID_PANEL_MEDIA_PLAYER_SENSOR_TYPE1 = "e3"
    FID_ROOM_TEMPERATURE_CONTROLLER_WITH_FAN_TYPE1 = "e4"
    FID_ROOM_TEMPERATURE_CONTROLLER_WITHOUT_FAN_TYPE1 = "e5"
    FID_HEATING_ACTUATOR_TYPE1 = "e6"
    FID_TWO_LEVEL_HEATING_ACTUATOR_TYPE1 = "e7"
    FID_COOLING_ACTUATOR_TYPE1 = "e8"
    FID_TWO_LEVEL_COOLING_ACTUATOR_TYPE1 = "e9"
    FID_HEATING_COOLING_ACTUATOR_TYPE1 = "ea"
    FID_TWO_LEVEL_HEATING_COOLING_ACTUATOR_TYPE1 = "eb"
    FID_RGB_CT_ACTUATOR_TYPE8 = "ec"
    FID_ROOM_TEMPERATURE_CONTROLLER_PROXY_WITHOUT_FAN = "ed"
    FID_ROOM_TEMPERATURE_CONTROLLER_EXTENSION_PROXY = "ee"
    FID_HVAC_WITH_ENERGY = "ef"
    FID_SWITCH_SENSOR_ROCKER_TYPE0 = "1000"
    FID_SWITCH_SENSOR_ROCKER_TYPE1 = "1001"
    FID_SWITCH_SENSOR_ROCKER_TYPE2 = "1002"
    FID_SWITCH_SENSOR_PUSHBUTTON_TYPE0 = "1008"
    FID_SWITCH_SENSOR_PUSHBUTTON_TYPE1 = "1009"
    FID_SWITCH_SENSOR_PUSHBUTTON_TYPE2 = "100a"
    FID_SWITCH_SENSOR_PUSHBUTTON_TYPE3 = "100b"
    FID_SWITCH_SENSOR_PUSHBUTTON_TYPE4 = "100c"
    FID_DIMMING_SENSOR_ROCKER_TYPE0 = "1010"
    FID_DIMMING_SENSOR_ROCKER_TYPE1 = "1011"
    FID_DIMMING_SENSOR_ROCKER_TYPE2 = "1012"
    FID_DIMMING_SENSOR_PUSHBUTTON_TYPE0 = "1018"
    FID_DIMMING_SENSOR_PUSHBUTTON_TYPE1 = "1019"
    FID_DIMMING_SENSOR_PUSHBUTTON_TYPE2 = "101a"
    FID_DIMMING_SENSOR_PUSHBUTTON_TYPE3 = "101b"
    FID_STAIRCASE_LIGHT_SENSOR_ROCKER_TYPE0 = "1020"
    FID_STAIRCASE_LIGHT_SENSOR_ROCKER_TYPE1 = "1021"
    FID_STAIRCASE_LIGHT_SENSOR_ROCKER_TYPE2 = "1022"
    FID_STAIRCASE_LIGHT_SENSOR_PUSHBUTTON_TYPE0 = "1028"
    FID_STAIRCASE_LIGHT_SENSOR_PUSHBUTTON_TYPE1 = "1029"
    FID_STAIRCASE_LIGHT_SENSOR_PUSHBUTTON_TYPE2 = "102a"
    FID_STAIRCASE_LIGHT_SENSOR_PUSHBUTTON_TYPE3 = "102b"
    FID_SCENE_SENSOR_ROCKER_TYPE0 = "1030"
    FID_SCENE_SENSOR_ROCKER_TYPE1 = "1031"
    FID_SCENE_SENSOR_ROCKER_TYPE2 = "1032"
    FID_SCENE_SENSOR_PUSHBUTTON_TYPE0 = "1038"
    FID_SCENE_SENSOR_PUSHBUTTON_TYPE1 = "1039"
    FID_SCENE_SENSOR_PUSHBUTTON_TYPE2 = "103a"
    FID_SCENE_SENSOR_PUSHBUTTON_TYPE3 = "103b"
    FID_BLIND_SENSOR_ROCKER_TYPE0 = "1040"
    FID_BLIND_SENSOR_ROCKER_TYPE1 = "1041"
    FID_BLIND_SENSOR_ROCKER_TYPE2 = "1042"
    FID_BLIND_SENSOR_PUSHBUTTON_TYPE0 = "1048"
    FID_BLIND_SENSOR_PUSHBUTTON_TYPE1 = "1049"
    FID_BLIND_SENSOR_PUSHBUTTON_TYPE2 = "104a"
    FID_BLIND_SENSOR_PUSHBUTTON_TYPE3 = "104b"
    FID_FORCE_ON_OFF_SENSOR_ROCKER_TYPE0 = "1050"
    FID_FORCE_ON_OFF_SENSOR_ROCKER_TYPE1 = "1051"
    FID_FORCE_ON_OFF_SENSOR_ROCKER_TYPE2 = "1052"
    FID_FORCE_ON_OFF_SENSOR_PUSHBUTTON_TYPE0 = "1058"
    FID_FORCE_ON_OFF_SENSOR_PUSHBUTTON_TYPE1 = "1059"
    FID_FORCE_ON_OFF_SENSOR_PUSHBUTTON_TYPE2 = "105a"
    FID_FORCE_ON_OFF_SENSOR_PUSHBUTTON_TYPE3 = "105b"
    FID_FORCE_ON_OFF_SENSOR_PUSHBUTTON_TYPE4 = "105c"
    FID_FORCE_UP_DOWN_SENSOR_ROCKER_TYPE0 = "1060"
    FID_FORCE_UP_DOWN_SENSOR_ROCKER_TYPE1 = "1061"
    FID_FORCE_UP_DOWN_SENSOR_ROCKER_TYPE2 = "1062"
    FID_FORCE_UP_DOWN_SENSOR_PUSHBUTTON_TYPE0 = "1068"
    FID_FORCE_UP_DOWN_SENSOR_PUSHBUTTON_TYPE1 = "1069"
    FID_FORCE_UP_DOWN_SENSOR_PUSHBUTTON_TYPE2 = "106a"
    FID_FORCE_UP_DOWN_SENSOR_PUSHBUTTON_TYPE3 = "106b"
    FID_FORCE_UP_DOWN_SENSOR_PUSHBUTTON_TYPE4 = "106c"
    FID_TIMER_ACTION_SENSOR_ROCKER_TYPE0 = "1070"
    FID_TIMER_ACTION_SENSOR_ROCKER_TYPE1 = "1071"
    FID_TIMER_ACTION_SENSOR_ROCKER_TYPE2 = "1072"
    FID_TIMER_ACTION_SENSOR_PUSHBUTTON_TYPE0 = "1078"
    FID_TIMER_ACTION_SENSOR_PUSHBUTTON_TYPE1 = "1079"
    FID_TIMER_ACTION_SENSOR_PUSHBUTTON_TYPE2 = "107a"
    FID_TIMER_ACTION_SENSOR_PUSHBUTTON_TYPE3 = "107b"
    FID_TIMER_ACTION_SENSOR_PUSHBUTTON_TYPE4 = "107c"
    FID_SWITCH_FORCE_ON_OFF_SENSOR_ROCKER_TYPE0 = "1080"
    FID_SWITCH_FORCE_ON_OFF_SENSOR_ROCKER_TYPE1 = "1081"
    FID_MOVEMENT_DETECTOR_TYPE0 = "1090"
    FID_MOVEMENT_DETECTOR_SLAVE_TYPE0 = "1091"
    FID_MOVEMENT_DETECTOR_TYPE2 = "1092"
    FID_MOVEMENT_DETECTOR_TYPE3 = "1093"
    FID_MOVEMENT_DETECTOR_TYPE4 = "1094"
    FID_MOVEMENT_DETECTOR_SLAVE_TYPE3 = "1095"
    FID_MOVEMENT_DETECTOR_SLAVE_TYPE4 = "1096"
    FID_MEDIA_PLAYBACK_CONTROL_SENSOR_ROCKER_TYPE0 = "10a0"
    FID_MEDIA_PLAYBACK_CONTROL_SENSOR_ROCKER_TYPE1 = "10a1"
    FID_MEDIA_PLAYBACK_CONTROL_SENSOR_ROCKER_TYPE2 = "10a2"
    FID_MEDIA_PLAY_PAUSE_SENSOR_PUSHBUTTON_TYPE0 = "10a8"
    FID_MEDIA_PLAY_PAUSE_SENSOR_PUSHBUTTON_TYPE1 = "10a9"
    FID_MEDIA_PLAY_PAUSE_SENSOR_PUSHBUTTON_TYPE2 = "10aa"
    FID_MEDIA_PLAY_PAUSE_SENSOR_PUSHBUTTON_TYPE3 = "10ab"
    FID_MEDIA_VOLUME_SENSOR_ROCKER_TYPE0 = "10b0"
    FID_MEDIA_VOLUME_SENSOR_ROCKER_TYPE1 = "10b1"
    FID_MEDIA_VOLUME_SENSOR_ROCKER_TYPE2 = "10b2"
    FID_MEDIA_VOLUME_UP_SENSOR_PUSHBUTTON_TYPE0 = "10b8"
    FID_MEDIA_VOLUME_UP_SENSOR_PUSHBUTTON_TYPE1 = "10b9"
    FID_MEDIA_VOLUME_UP_SENSOR_PUSHBUTTON_TYPE2 = "10ba"
    FID_MEDIA_VOLUME_UP_SENSOR_PUSHBUTTON_TYPE3 = "10bb"
    FID_MEDIA_VOLUME_DOWN_SENSOR_PUSHBUTTON_TYPE0 = "10c0"
    FID_MEDIA_VOLUME_DOWN_SENSOR_PUSHBUTTON_TYPE1 = "10c1"
    FID_MEDIA_VOLUME_DOWN_SENSOR_PUSHBUTTON_TYPE2 = "10c2"
    FID_MEDIA_VOLUME_DOWN_SENSOR_PUSHBUTTON_TYPE3 = "10c3"
    FID_MEDIA_NEXT_FAVORITE_SENSOR_PUSHBUTTON_TYPE0 = "10c8"
    FID_MEDIA_NEXT_FAVORITE_SENSOR_PUSHBUTTON_TYPE1 = "10c9"
    FID_MEDIA_NEXT_FAVORITE_SENSOR_PUSHBUTTON_TYPE2 = "10ca"
    FID_MEDIA_NEXT_FAVORITE_SENSOR_PUSHBUTTON_TYPE3 = "10cb"
    FID_MEDIA_NEXT_SONG_SENSOR_PUSHBUTTON_TYPE0 = "10d0"
    FID_MEDIA_NEXT_SONG_SENSOR_PUSHBUTTON_TYPE1 = "10d1"
    FID_MEDIA_NEXT_SONG_SENSOR_PUSHBUTTON_TYPE2 = "10d2"
    FID_MEDIA_NEXT_SONG_SENSOR_PUSHBUTTON_TYPE3 = "10d3"
    FID_MEDIA_PREVIOUS_SONG_SENSOR_PUSHBUTTON_TYPE0 = "10d8"
    FID_MEDIA_PREVIOUS_SONG_SENSOR_PUSHBUTTON_TYPE1 = "10d9"
    FID_MEDIA_PREVIOUS_SONG_SENSOR_PUSHBUTTON_TYPE2 = "10da"
    FID_MEDIA_PREVIOUS_SONG_SENSOR_PUSHBUTTON_TYPE3 = "10db"
    FID_MWIRE_SWITCH_INPUT_TYPE0 = "10e0"
    FID_MWIRE_SWITCH_OUTPUT_TYPE0 = "10e8"
    FID_MWIRE_SWITCH_OUTPUT_TYPE1 = "10e9"
    FID_MWIRE_BLIND_INPUT_TYPE0 = "10f0"
    FID_MWIRE_BLIND_OUTPUT_TYPE0 = "10f8"
    FID_MWIRE_BLIND_OUTPUT_TYPE1 = "10f9"
    FID_MWIRE_MOVEMENT_INPUT_TYPE0 = "1100"
    FID_MWIRE_MOVEMENT_OUTPUT_TYPE0 = "1108"
    FID_MWIRE_PRESET_INPUT_TYPE0 = "1110"
    FID_MWIRE_PRESET_OUTPUT_TYPE0 = "1118"
    FID_MWIRE_PRESET_OUTPUT_TYPE1 = "1119"
    FID_MWIRE_SWITCH_REMOTE_CONTROL_ROCKER = "1120"
    FID_MWIRE_BLIND_REMOTE_CONTROL_ROCKER = "1130"
    FID_MWIRE_PRESET_REMOTE_CONTROL_ROCKER = "1140"
    FID_MWIRE_DIMMING_INPUT_TYPE0 = "1150"
    FID_PRESENCE_DETECTOR_TYPE0 = "1160"
    FID_PRESENCE_DETECTOR_TYPE1 = "1161"
    FID_LOCK_SENSOR_SENSOR_ROCKER_TYPE0 = "1170"
    FID_LOCK_SENSOR_SENSOR_ROCKER_TYPE1 = "1171"
    FID_LOCK_SENSOR_SENSOR_ROCKER_TYPE2 = "1172"
    FID_LOCK_SENSOR_SENSOR_PUSHBUTTON_TYPE0 = "1178"
    FID_LOCK_SENSOR_SENSOR_PUSHBUTTON_TYPE1 = "1179"
    FID_LOCK_SENSOR_SENSOR_PUSHBUTTON_TYPE2 = "117a"
    FID_LOCK_SENSOR_SENSOR_PUSHBUTTON_TYPE3 = "117b"
    FID_TEMPERATURE_ADJUSTMENT_SENSOR_ROCKER_TYPE0 = "1180"
    FID_OPERATION_MODE_ADJUSTMENT_SENSOR_ROCKER_TYPE0 = "1190"
    FID_OPERATION_MODE_ADJUSTMENT_SENSOR_PUSHBUTTON_TYPE2 = "11a2"
    FID_SWITCH_ACTUATOR_TYPE8 = "1808"
    FID_SWITCH_ACTUATOR_TYPE9 = "1809"
    FID_DIMMING_ACTUATOR_TYPE0 = "1810"
    FID_DIMMING_ACTUATOR_TYPE8 = "1818"
    FID_DIMMING_ACTUATOR_TYPE9 = "1819"
    FID_BLINDS_ACTUATOR_TYPE0 = "1820"
    FID_BLINDS_ACTUATOR_TYPE1 = "1821"
    FID_BLINDS_ACTUATOR_TYPE2 = "1822"
    FID_BLINDS_ACTUATOR_TYPE3 = "1823"
    FID_BLINDS_ACTUATOR_TYPE5 = "1825"
    FID_E_CONTACT_SWITCH_ACTUATOR_TYPE0 = "1830"
    FID_VENTILATION_SWITCH_ACTUATOR_TYPE0 = "1840"
    FID_HOUSEKEEPING_TYPE0 = "1f00"
    FID_HOUSEKEEPING_TYPE1 = "1f01"
    FID_LIGHT_GROUP = "4000"
    FID_BLIND_GROUP = "4001"
    FID_DIMMER_GROUP = "4002"
    FID_RGB_W_GROUP = "4003"
    FID_SACE_BLIND_GROUP = "4004"
    FID_SHUTTER_GROUP = "4005"
    FID_RGB_GROUP = "4006"
    FID_RGBW_GROUP = "4007"
    FID_LOCK_SENSOR_GROUP = "4008"
    FID_SCENE = "4800"
    FID_SPECIAL_SCENE_PANIC = "4801"
    FID_SPECIAL_SCENE_ALL_OFF = "4802"
    FID_SPECIAL_SCENE_ALL_BLINDS_UP = "4803"
    FID_SPECIAL_SCENE_ALL_BLINDS_DOWN = "4804"
    FID_TIMER_PROGRAM_SWITCH_ACTUATOR = "4a00"
    FID_ALERT_SWITCH_ACTUATOR = "4a01"
    FID_MOVEMENT_DETECTOR_ICON2 = "f5fa"
    FID_DALI_ACTUATOR_ICON = "f5fb"
    FID_SUPER_DEVICE_ICON = "f6fe"
    FID_83221_ICON = "f8fd"
    FID_PILL_DEVICE = "f9fb"
    FID_SU_F_4_0_PB_1_ICON = "fbff"
    FID_SU_F_2_0_PB_1_ICON = "fcff"
    FID_KEYPAD_DEVICE = "fee4"
    FID_SIMPLE_ROCKER_DEVICE = "fee5"
    FID_DIMMER_ROCKER_DEVICE = "fee6"
    FID_THERMOSTAT_DEVICE = "fee7"
    FID_CEILING_FAN_DEVICE = "fee8"
    FID_WEATHER_STATION_DEVICE = "feef"
    FID_HUE_DEVICE = "fef0"
    FID_ACTUATOR_DEVICE = "fefb"
    FID_MOVEMENT_DETECTOR_DEVICE = "fefc"
    FID_PANEL_SENSOR = "fefd"
    FID_REG_DEVICE = "fefe"
    FID_PANEL_DEVICE = "feff"
    FID_RTC_DEVICE = "ff00"
    FID_ROCKER_SENSOR = "ff01"
    FID_KEYPAD_ICON = "ffe4"
    FID_SIMPLE_ROCKER_ICON = "ffe5"
    FID_DIMMER_ROCKER_ICON = "ffe6"
    FID_THERMOSTAT_ICON = "ffe7"
    FID_CEILING_FAN_ACTUATOR_ICON = "ffe8"
    FID_MEDIA_PLAYER_ICON = "ffe9"
    FID_WINDOW_SENSOR_ICON = "ffea"
    FID_BINARY_SENSOR_ICON = "ffeb"
    FID_SOLAR_ICON = "ffec"
    FID_WEATHER_STATION_ICON = "ffed"
    FID_HUE_ICON = "ffee"
    FID_REG_HEATING_ACTUATOR_ICON = "ffef"
    FID_REG_BINARY_OUTPUT_ICON = "fff0"
    FID_REG_BINARY_INPUT_ICON = "fff1"
    FID_REG_SHUTTER_ICON = "fff2"
    FID_REG_SWITCH_ICON = "fff3"
    FID_REG_DIMMER_ICON = "fff4"
    FID_MOVEMENT_DETECTOR_ICON = "fff5"
    FID_RTC_ICON = "fff6"
    FID_4_INCH_PANEL_ICON = "fff7"
    FID_7_INCH_PANEL_ICON = "fff8"
    FID_PILL_ICON = "fff9"
    FID_DIN_RAIL_DEVICE_ICON = "fffa"
    FID_4_PUSH_BUTTON_SENSOR_ICON = "fffb"
    FID_2_PUSH_BUTTON_SENSOR_ICON = "fffc"
    FID_2_ROCKER_SWITCH_SENSOR_ICON = "fffe"
    FID_1_ROCKER_SWITCH_SENSOR_ICON = "ffff"


def load_functions_from_json_file(file_path: str):
    """
    Load functions from a json file.

    This will print the functions enum for easier ingestion into the FunctionId class
    It expects an array json file in the format of  Function ID (dec) and Name.
    Use this output to populate the function ids
    See: https://developer.eu.mybuildings.abb.com/fah_local/reference/functionids
    :param file_path: Path of the JSON file.

    The api "seems" to return the hex value, but it doesn't include `0x` and
    truncates any leading 0's. It also returns the value all lowercase vs all uppercase.

    This included function attempts to match that logic, but as I see it as a bug it
    could be patched in a future version of the SysAP and break this lookup.
    """
    import json

    with open(file_path) as functions_file:
        _functions = json.load(functions_file)

    for function in _functions:
        _id = function.get("Function ID (hex)").replace("0x", "").lstrip("0").lower()
        if _id == "":
            _id = "0"
        print(f'    {function.get("Name")} = \'{_id}\'')  # noqa: T201
