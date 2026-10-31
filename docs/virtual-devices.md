# Virtual devices

This reference lists **40 SysAP virtual-device types**, including **11 with matching library classes**.[^source]

Use the API type as the creation payload's `type`. Channels are listed with their hexadecimal function IDs; **Not implemented** means the SysAP supports the device but the library has no matching virtual-channel class.

Function names match the [`Function` enum](../src/abbfreeathome/bin/function.py); **Not defined** means the ID is absent from that enum.

| API type | Channel (function ID) | Function name | Library class |
| --- | --- | --- | --- |
| `AirQualityCO` | `ch0000` (`e019`) | Not defined | Not implemented |
| `AirQualityCO2` | `ch0000` (`e018`) | Not defined | Not implemented |
| `AirQualityHumidity` | `ch0000` (`b03f`) | Not defined | Not implemented |
| `AirQualityNO2` | `ch0000` (`e01a`) | Not defined | Not implemented |
| `AirQualityO3` | `ch0000` (`e01b`) | Not defined | Not implemented |
| `AirQualityPM10` | `ch0000` (`e01c`) | Not defined | Not implemented |
| `AirQualityPM25` | `ch0000` (`e01d`) | Not defined | Not implemented |
| `AirQualityPressure` | `ch0000` (`e017`) | Not defined | Not implemented |
| `AirQualityTemperature` | `ch0000` (`0043`) | `FID_TEMPERATURE_SENSOR` | `VirtualTemperatureSensor` |
| `AirQualityVOC` | `ch0000` (`e01e`) | Not defined | Not implemented |
| `BinarySensor` | `ch0000` (`0000`) | `FID_SWITCH_SENSOR` | Not implemented |
| `BlindActuator` | `ch0000` (`0061`) | `FID_BLIND_ACTUATOR` | Not implemented |
| `CeilingFanActuator` | `ch0000` (`0073`) | `FID_CEILING_FAN_ACTUATOR` | Not implemented |
| `CODetector` | `ch0000` (`007e`) | `FID_CARBON_MONOXIDE_SENSOR` | Not implemented |
| `DimActuator` | `ch0000` (`0012`) | `FID_DIMMING_ACTUATOR` | `VirtualDimmingActuator` |
| `EnergyBattery` | `ch0000` (`0050`) | `FID_BATTERY_INFO` | Not implemented |
| `EnergyInverter` | `ch0000` (`004e`) | `FID_INVERTER_INFO` | Not implemented |
| `EnergyInverterBattery` | `ch0000` (`00b2`) | `FID_INVERTER_BATTERY` | Not implemented |
| `EnergyInverterMeter` | `ch0000` (`00b0`) | `FID_INVERTER_METER` | Not implemented |
| `EnergyInverterMeterBattery` | `ch0000` (`00af`) | `FID_INVERTER_METER_BATTERY` | Not implemented |
| `EnergyMeter` | `ch0000` (`004f`) | `FID_METER_INFO` | Not implemented |
| `EnergyMeterBattery` | `ch0000` (`00b1`) | `FID_METER_BATTERY` | Not implemented |
| `EnergyMeterv2`[^energy] | `ch0001` (`00c5`)<br>`ch0002` (`00c7`)<br>`ch0003` (`00c6`) | `FID_ENERGY_TWO_WAY_METER`<br>`FID_ENERGY_BATTERY`<br>`FID_ENERGY_INVERTER` | `VirtualEnergyTwoWayMeter`<br>`VirtualEnergyBattery`<br>`VirtualEnergyInverter` |
| `evcharging` | `ch0000` (`00a6`) | `FID_WALLBOX` | Not implemented |
| `FireDetector` | `ch0000` (`007d`) | `FID_SMOKE_DETECTOR` | Not implemented |
| `HomeAppliance-Laundry` | `ch0000` (`0069`) | `FID_LAUNDRY` | Not implemented |
| `HVAC` | `ch0000` (`00b7`) | `FID_HVAC` | Not implemented |
| `MediaPlayer` | `ch0000` (`005a`) | `FID_MEDIA_PLAYER` | Not implemented |
| `RTC` | `ch0000` (`0023`) | `FID_ROOM_TEMPERATURE_CONTROLLER_MASTER_WITHOUT_FAN` | `VirtualRoomTemperatureController` |
| `ShutterActuator` | `ch0000` (`0009`) | `FID_SHUTTER_ACTUATOR` | Not implemented |
| `simple_doorlock` | `ch0000` (`00a8`) | `FID_DOOR_LOCK_CONTROL` | Not implemented |
| `SplitUnit` | `ch0001` (`00f1`) | `FID_SPLIT_UNIT` | Not implemented |
| `SwitchingActuator` | `ch0000` (`0007`) | `FID_SWITCH_ACTUATOR` | `VirtualSwitchActuator` |
| `Weather-BrightnessSensor` | `ch0000` (`0041`) | `FID_BRIGHTNESS_SENSOR` | `VirtualBrightnessSensor` |
| `Weather-RainSensor` | `ch0000` (`0042`) | `FID_RAIN_SENSOR` | `VirtualRainSensor` |
| `Weather-TemperatureSensor` | `ch0000` (`0043`) | `FID_TEMPERATURE_SENSOR` | `VirtualTemperatureSensor` |
| `Weather-WindSensor` | `ch0000` (`0044`) | `FID_WIND_SENSOR` | `VirtualWindSensor` |
| `WeatherStation` | `ch0000` (`0041`)<br>`ch0001` (`0042`)<br>`ch0002` (`0043`)<br>`ch0003` (`0044`) | `FID_BRIGHTNESS_SENSOR`<br>`FID_RAIN_SENSOR`<br>`FID_TEMPERATURE_SENSOR`<br>`FID_WIND_SENSOR` | `VirtualBrightnessSensor`<br>`VirtualRainSensor`<br>`VirtualTemperatureSensor`<br>`VirtualWindSensor` |
| `WindowActuator` | `ch0000` (`0062`) | `FID_ATTIC_WINDOW_ACTUATOR` | Not implemented |
| `WindowSensor` | `ch0000` (`000f`) | `FID_WINDOW_DOOR_SENSOR` | `VirtualWindowDoorSensor` |

[^source]: Based on [data collected](https://gist.github.com/kingsleyadam/91fcd0743ed9e4e6fc10ee57dc2f9cf1) on one SysAP on 2026-10-30 with firmware 3.5.4 and local-abbfreeathome 3.10.0. Channel loading was verified, not command/feedback operation; availability may vary by firmware. Of 42 advertised types, `KNX-SwitchSensor` and `AirQualityFull` were rejected and are excluded. `Trigger` was not advertised and no type produced the library's `VirtualTrigger` channel (`0045`).

[^energy]: Channels shown use properties `flavor: "E"` and `capabilities: [16, 17, 18, 19, 22, 28]`; other combinations were not tested. Capability IDs are distinct from channel function IDs.
