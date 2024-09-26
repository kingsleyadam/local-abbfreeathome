"""
Defines the avaliable paiarings in the Free@Home System.

See: https://developer.eu.mybuildings.abb.com/fah_local/reference/pairingids
"""

import enum


class PairingId(enum.Enum):
    """An Enum class for all Free@Home Parings."""

    AL_INVALID = 0
    AL_SWITCH_ON_OFF = 1
    AL_TIMED_START_STOP = 2
    AL_FORCED = 3
    AL_SCENE_CONTROL = 4
    AL_DOOR_OPENER = 5
    AL_TIMED_MOVEMENT = 6
    AL_TIMED_PRESENCE = 7
    AL_RELATIVE_SET_VALUE_CONTROL = 16
    AL_ABSOLUTE_SET_VALUE_CONTROL = 17
    AL_NIGHT = 18
    AL_RESET_ERROR = 19
    AL_NIGHT_ACTUATOR_FOR_SYSAP = 20
    AL_RGB = 21
    AL_COLOR_TEMPERATURE = 22
    AL_HSV = 23
    AL_COLOR = 24
    AL_SATURATION = 25
    AL_ABSOLUTE_SET_VALUE_CONTROL_HUE = 26
    AL_MOVE_UP_DOWN = 32
    AL_STOP_STEP_UP_DOWN = 33
    AL_DEDICATED_STOP = 34
    AL_SET_ABSOLUTE_POSITION_BLINDS_PERCENTAGE = 35
    AL_SET_ABSOLUTE_POSITION_SLATS_PERCENTAGE = 36
    AL_WIND_ALARM = 37
    AL_FROST_ALARM = 38
    AL_RAIN_ALARM = 39
    AL_FORCED_UP_DOWN = 40
    AL_WINDOW_DOOR_POSITION = 41
    AL_ACTUATING_VALUE_HEATING = 48
    AL_FAN_COIL_LEVEL = 49
    AL_ACTUATING_VALUE_COOLING = 50
    AL_SET_POINT_TEMPERATURE = 51
    AL_RELATIVE_SET_POINT_TEMPERATURE = 52
    AL_WINDOW_DOOR = 53
    AL_STATE_INDICATION = 54
    AL_FAN_MANUAL_ON_OFF = 55
    AL_CONTROLLER_ON_OFF = 56
    AL_RELATIVE_SET_POINT_REQUEST = 57
    AL_ECO_ON_OFF = 58
    AL_COMFORT_TEMPERATURE = 59
    AL_ABSOLUTE_SET_VALUE_CONTROL_WHITE = 60
    AL_SELECTED_HEATING_COOLING_MODE_REQUEST = 61
    AL_INFO_HEATING_COOLING_MODE = 62
    AL_FAN_STAGE_REQUEST = 64
    AL_FAN_MANUAL_ON_OFF_REQUEST = 65
    AL_CONTROLLER_ON_OFF_REQUEST = 66
    AL_VALUE_ADDITIONAL_HEATING = 67
    AL_ECO_ON_OFF_INDICATION = 68
    AL_AWAY = 80
    AL_INFO_ON_OFF = 256
    AL_INFO_FORCE = 257
    AL_SYSAP_INFO_ON_OFF = 261
    AL_SYSAP_INFO_FORCE = 262
    AL_INFO_ACTUAL_DIMMING_VALUE = 272
    AL_INFO_ERROR = 273
    AL_SYSAP_INFO_ACTUAL_DIMMING_VALUE = 277
    AL_SYSAP_INFO_ERROR = 278
    AL_INFO_RGB = 279
    AL_INFO_COLOR_TEMPERATURE = 280
    AL_SYSAP_INFO_RGB = 281
    AL_SYSAP_INFO_COLOR_TEMPERATURE = 282
    AL_INFO_HSV = 283
    AL_SYSAP_INFO_HSV = 284
    AL_INFO_COLOR_MODE = 285
    AL_SYSAP_INFO_COLOR_MODE = 286
    AL_COLOR_MODE = 287
    AL_INFO_MOVE_UP_DOWN = 288
    AL_CURRENT_ABSOLUTE_POSITION_BLINDS_PERCENTAGE = 289
    AL_CURRENT_ABSOLUTE_POSITION_SLATS_PERCENTAGE = 290
    AL_VALID_CURRENT_ABSOLUTE_POSITION = 291
    AL_SYSAP_INFO_MOVE_UP_DOWN = 293
    AL_SYSAP_CURRENT_ABSOLUTE_POSITION_BLINDS_PERCENTAGE = 294
    AL_SYSAP_CURRENT_ABSOLUTE_POSITION_SLATS_PERCENTAGE = 295
    AL_CAPBP_AND_CAPSP_VALID = 296
    AL_MEASURED_TEMPERATURE = 304
    AL_INFO_VALUE_HEATING = 305
    AL_INFO_VALUE_COOLING = 306
    AL_RESET_OVERLOAD = 307
    AL_OVERLOAD_DETECTION = 308
    AL_HEATING_COOLING = 309
    AL_ACTUATING_FAN_STAGE_HEATING = 310
    AL_DEPRECATED_0137 = 311
    AL_DEPRECATED_0138 = 312
    AL_DEPRECATED_0139 = 313
    AL_INFO_ABSOLUTE_SET_POINT_REQUEST = 320
    AL_INFO_ACTUATING_VALUE_ADD_HEATING = 321
    AL_INFO_ACTUATING_VALUE_ADD_COOLING = 322
    AL_ACTUATING_VALUE_ADD_HEATING = 323
    AL_ACTUATING_VALUE_ADD_COOLING = 324
    AL_INFO_FAN_ACTUATING_STAGE_HEATING = 325
    AL_INFO_FAN_MANUAL_ON_OFF_HEATING = 326
    AL_ACTUATING_FAN_STAGE_COOLING = 327
    AL_DEPRECATED_0148 = 328
    AL_INFO_FAN_ACTUATING_STAGE_COOLING = 329
    AL_INFO_FAN_MANUAL_ON_OFF_COOLING = 330
    AL_HEATING_ACTIVE = 331
    AL_COOLING_ACTIVE = 332
    AL_HEATING_DEMAND = 333
    AL_COOLING_DEMAND = 334
    AL_INFO_HEATING_DEMAND = 335
    AL_INFO_COOLING_DEMAND = 336
    AL_HUMIDITY = 337
    AL_AUX_ON_OFF_REQUEST = 338
    AL_AUX_ON_OFF_RESPONSE = 339
    AL_HEATING_ON_OFF_REQUEST = 340
    AL_COOLING_ON_OFF_REQUEST = 341
    AL_INFO_OPERATION_MODE = 342
    AL_INFO_SWING_MODE = 343
    AL_SUPPORTED_FEATURES = 344
    AL_EXTENDED_STATUS = 345
    AL_EXTENDED_STATUS_US = 346
    AL_AUX_HEATING_ON_OFF_REQUEST = 347
    AL_EMERGENCY_HEATING_ON_OFF_REQUEST = 348
    AL_RELATIVE_FAN_SPEED_CONTROL = 352
    AL_ABSOLUTE_FAN_SPEED_CONTROL = 353
    AL_INFO_ABSOLUTE_FAN_SPEED = 354
    AL_SYSAP_INFO_ABSOLUTE_FAN_SPEED = 355
    AL_TIMED_MOVEMENT_REQUEST = 356
    AL_INFO_TIMED_MOVEMENT = 357
    AL_MOVEMENT_DETECTOR_STATUS = 358
    AL_LOCK_SENSOR = 359
    AL_INFO_LOCKED_SENSOR = 360
    AL_SYSAP_INFO_LOCKED_SENSOR = 361
    AL_INFO_VALUE_WHITE = 368
    AL_SYSAP_INFO_VALUE_WHITE = 369
    AL_NOTIFICATION_FLAGS = 416
    AL_INFO_LOCAL_TIMER_CONTROL_8 = 417
    AL_INFO_GROUP_TIMER_CONTROL_8 = 418
    AL_MWIRE_SWITCH_ON_OFF = 419
    AL_MWIRE_RELATIVE_SET_VALUE_CONTROL = 420
    AL_MWIRE_MOVE_UP_DOWN = 421
    AL_MWIRE_STOP_STEP_UP_DOWN = 422
    AL_MWIRE_PRESET = 423
    AL_INFO_LOCAL_TIMER_CONTROL_32 = 424
    AL_INFO_GROUP_TIMER_CONTROL_32 = 425
    AL_TRIGGERED_PIR_MASK = 426
    AL_TIMEFRAME_MOVEMENT = 427
    AL_TIMED_DIMMING = 428
    AL_INFO_TIMED_DIMMING = 429
    AL_DEPRECATED_0200 = 512
    AL_BOOL_VALUE_1 = 640
    AL_BOOL_VALUE_2 = 641
    AL_BOOL_VALUE_3 = 642
    AL_BOOL_VALUE_4 = 643
    AL_SCALING_VALUE_1 = 656
    AL_SCALING_VALUE_2 = 657
    AL_SCALING_VALUE_3 = 658
    AL_SCALING_VALUE_4 = 659
    AL_UNLOCK = 672
    AL_LOCATOR_BEEP = 704
    AL_SWITCH_TEST_ALARM = 705
    AL_TEST_ALARM_ACTIVE = 706
    AL_FIRE_ALARM_ACTIVE = 707
    AL_CO_ALARM_ACTIVE = 708
    AL_REMOTE_LOCATE = 709
    AL_DETECTOR_PAIRING_MODE = 710
    AL_INFO_DETECTOR_PAIRING_MODE = 711
    AL_FLOOD_ALARM = 712
    AL_SET_OPERATING_MODE = 768
    AL_HEATING_COOLING_DOMUS = 769
    AL_OUTDOOR_TEMPERATURE = 1024
    AL_WIND_FORCE = 1025
    AL_BRIGHTNESS_ALARM = 1026
    AL_BRIGHTNESS_LEVEL = 1027
    AL_WIND_SPEED = 1028
    AL_RAIN_SENSOR_ACTIVATION_PERCENTAGE = 1029
    AL_RAIN_SENSOR_FREQUENCY = 1030
    AL_MEDIA_PLAY = 1088
    AL_MEDIA_PAUSE = 1089
    AL_MEDIA_NEXT = 1090
    AL_MEDIA_PREVIOUS = 1091
    AL_MEDIA_PLAY_MODE = 1092
    AL_MEDIA_MUTE = 1093
    AL_RELATIVE_VOLUME_CONTROL = 1094
    AL_ABSOLUTE_VOLUME_CONTROL = 1095
    AL_GROUP_MEMBERSHIP = 1096
    AL_PLAY_FAVORITE = 1097
    AL_PLAY_NEXT_FAVORITE = 1098
    AL_PLAYBACK_STATUS = 1120
    AL_INFO_MEDIA_CURRENT_ITEM_METADATA = 1121
    AL_INFO_MUTE = 1122
    AL_INFO_ACTUAL_VOLUME = 1123
    AL_ALLOWED_PLAYBACK_ACTIONS = 1124
    AL_INFO_GROUP_MEMBERSHIP = 1125
    AL_INFO_PLAYING_FAVORITE = 1126
    AL_ABSOLUTE_GROUP_VOLUME_CONTROL = 1127
    AL_INFO_ABSOLUTE_GROUP_VOLUME = 1128
    AL_INFO_CURRENT_MEDIA_SOURCE = 1129
    AL_SOLAR_POWER_PRODUCTION = 1184
    AL_INVERTER_OUTPUT_POWER = 1185
    AL_SOLAR_ENERGY_TODAY = 1186
    AL_INJECTED_ENERGY_TODAY = 1187
    AL_PURCHASED_ENERGY_TODAY = 1188
    AL_NOTIFICATION_RUN_STANDALONE = 1189
    AL_SELF_CONSUMPTION = 1190
    AL_SELF_SUFFICIENCY = 1191
    AL_HOME_POWER_CONSUMPTION = 1192
    AL_POWER_TO_GRID = 1193
    AL_CONSUMED_ENERGY_TODAY = 1194
    AL_NOTIFICATION_METER_COMMUNICATION_ERROR_WARNING = 1195
    AL_SOC = 1196
    AL_BATTERY_POWER = 1197
    AL_BOOST_ENABLE_REQUEST = 1200
    AL_SWITCH_CHARGING = 1201
    AL_STOP_ENABLE_CHARGING_REQUEST = 1202
    AL_INFO_BOOST = 1203
    AL_INFO_WALLBOX_STATUS = 1204
    AL_INFO_CHARGING = 1205
    AL_INFO_CHARGING_ENABLED = 1206
    AL_INFO_INSTALLED_POWER = 1207
    AL_INFO_ENERGY_TRANSMITTED = 1208
    AL_INFO_CAR_RANGE = 1209
    AL_INFO_START_OF_CHARGING_SESSION = 1210
    AL_INFO_LIMIT_FOR_CHARGER = 1211
    AL_INFO_LIMIT_FOR_CHARGER_GROUP = 1212
    AL_INFO_ALBUM_COVER_URL = 1213
    AL_INFO_CURRENT_SOLAR_POWER = 1214
    AL_INFO_CURRENT_INVERTER_OUTPUT_POWER = 1215
    AL_INFO_CURRENT_HOME_POWER_CONSUMPTION = 1216
    AL_INFO_CURRENT_POWER_TO_GRID = 1217
    AL_INFO_CURRENT_BATTERY_POWER = 1218
    AL_INFO_TOTAL_ENERGY_FROM_GRID = 1219
    AL_INFO_TOTAL_ENERGY_TO_GRID = 1220
    AL_MEASURED_CURRENT_POWER_CONSUMED = 1221
    AL_MEASURED_IMPORTED_ENERGY_TODAY = 1222
    AL_MEASURED_EXPORTED_ENERGY_TODAY = 1223
    AL_MEASURED_TOTAL_ENERGY_IMPORTED = 1224
    AL_MEASURED_TOTAL_ENERGY_EXPORTED = 1225
    AL_SWITCH_ECO_CHARGING_ON_OFF = 1226
    AL_INFO_ECO_CHARGING_ON_OFF = 1227
    AL_LIMIT_FOR_CHARGER = 1228
    AL_MEASURED_CURRENT_EXCESS_POWER = 1229
    AL_MEASURED_TOTAL_WATER = 1230
    AL_MEASURED_TOTAL_GAS = 1231
    AL_CONSUMED_WATER_TODAY = 1232
    AL_CONSUMED_GAS_TODAY = 1233
    AL_MEASURED_VOLTAGE = 1234
    AL_MEASURED_CURRENT = 1235
    AL_SYSTEM_STATE_DOMUS = 1280
    AL_DISARM_SYSTEM = 1281
    AL_DISARM_COUNTER = 1282
    AL_SMS_TRIGGER_EVENT = 1283
    AL_INFO_INTRUSION_ALARM = 1284
    AL_INFO_SAFETY_ALARM = 1285
    AL_ARMED = 1286
    AL_INFO_ERROR_STATUS = 1287
    AL_ENABLE_CONFIGURATION = 1288
    AL_DOMUS_ZONE_CONTROL = 1289
    AL_DOMUS_KEY_INFO = 1290
    AL_ZONE_STATUS = 1291
    AL_SENSOR_STATUS = 1292
    AL_INFO_CONFIGURATION_STATUS = 1293
    AL_DOMUS_DISARM_DELAY_TIME = 1294
    AL_DOMUS_IM_ALARM = 1488
    AL_DOMUS_IM_ALARM_FEEDBACK = 1489
    AL_DOMUS_IM_SAFETY = 1490
    AL_DOMUS_IM_SAFETY_FEEDBACK = 1491
    AL_DOMUS_IM_SIREN = 1492
    AL_DOMUS_IM_REMOTE = 1493
    AL_DOMUS_IM_REMOTE_FEEDBACK = 1494
    AL_DOMUS_REMOTE_TRIGGER = 1495
    AL_DOMUS_SIGNAL_STRENGTH = 1496
    AL_START_STOP = 1536
    AL_PAUSE_RESUME = 1537
    AL_SELECT_PROGRAM = 1538
    AL_DELAYED_START_TIME = 1539
    AL_INFO_STATUS = 1540
    AL_INFO_REMOTE_START_ENABLED = 1541
    AL_INFO_PROGRAM = 1542
    AL_INFO_FINISH_TIME = 1543
    AL_INFO_DELAYED_START_TIME = 1544
    AL_INFO_DOOR = 1545
    AL_INFO_DOOR_ALARM = 1546
    AL_SWITCH_SUPERCOOL = 1547
    AL_SWITCH_SUPERFREEZE = 1548
    AL_INFO_SWITCH_SUPERCOOL = 1549
    AL_INFO_SWITCH_SUPERFREEZE = 1550
    AL_CURRENT_TEMPERATURE_APPLIANCE_1 = 1551
    AL_CURRENT_TEMPERATURE_APPLIANCE_2 = 1552
    AL_SETPOINT_TEMPERATURE_APPLIANCE_1 = 1553
    AL_SETPOINT_TEMPERATURE_APPLIANCE_2 = 1554
    AL_CHANGE_OPERATION = 1555
    AL_INFO_VERBOSE_STATUS = 1556
    AL_INFO_REMAINING_TIME = 1557
    AL_INFO_STATUS_CHANGED_TIME = 1558
    AL_ACTIVE_ENERGY_V64 = 1559
    AL_LOCK_UNLOCK_COMMAND = 1560
    AL_INFO_LOCK_UNLOCK_COMMAND = 1561
    AL_INFO_PRESSURE = 1562
    AL_INFO_CO_2 = 1563
    AL_INFO_CO = 1564
    AL_INFO_NO_2 = 1565
    AL_INFO_O_3 = 1566
    AL_INFO_PM_10 = 1567
    AL_INFO_PM_2_5 = 1568
    AL_INFO_VOC = 1569
    AL_INFO_VOC_INDEX = 1570
    AL_TRIGGER_CAMERA_CONFIG = 1571
    AL_INFO_CAMERA_CONFIG = 1574
    AL_INFO_CAMERA_ID = 1575
    AL_CO2_ALERT = 1576
    AL_VOC_ALERT = 1577
    AL_HUMIDITY_ALERT = 1578
    AL_AUTONOMOUS_SWITCH_OFF_TIME = 1579
    AL_INFO_AUTONOMOUS_SWITCH_OFF_TIME = 1580
    AL_INFO_PLAYLIST = 1581
    AL_INFO_AUDIO_INPUT = 1582
    AL_SELECT_PROFILE = 1583
    AL_TIME_OF_DAY = 61441
    AL_DATE = 61442
    AL_MESSAGE_CENTER_NOTIFICATION = 61443
    AL_SWITCH_ENTITY_ON_OFF = 61697
    AL_INFO_SWITCH_ENTITY_ON_OFF = 61698
    AL_CONSISTENCY_TAG = 61700
    AL_BATTERY_STATUS = 61701
    AL_STAY_AWAKE = 61702
    AL_CYCLIC_SLEEP_TIME = 61707
    AL_SYSAP_PRESENCE = 61708
    AL_SYSAP_TEMPERATURE = 61709
    AL_STANDBY_STATISTICS = 61710
    AL_HEARTBEAT_DELAY = 61711
    AL_INFO_HEARTBEAT_DELAY = 61712
    AL_MEASURED_TEMPERATURE_1 = 65281
    AL_MEASURED_TEMPERATURE_2 = 65282
    AL_MEASURED_TEMPERATURE_3 = 65283
    AL_MEASURED_TEMPERATURE_4 = 65284
    AL_IGNORE = 65534


def load_pairings_from_json_file(file_path: str):
    """
    Load parings from a json file.

    This will print the pairing id enum for easier ingestion into the PairingId class
    It expects an array json file in the format of  Pairing ID (dec) and Name.
    Use this output to populate the function ids
    See: https://developer.eu.mybuildings.abb.com/fah_local/reference/pairingids
    :param file_path: Path of the JSON file.
    """
    import json

    with open(file_path) as pairings_file:
        _pairings = json.load(pairings_file)

    for pairing in _pairings:
        if pairing.get("Name"):
            print(  # noqa: T201
                f'    {pairing.get("Name")} = {pairing.get("Pairing ID (dec)")}'
            )
