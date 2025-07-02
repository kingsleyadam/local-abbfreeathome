# Python Package - ABB Free@Home via Local Api

[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/kingsleyadam/local-abbfreeathome)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/local-abbfreeathome)
![PyPI - Version](https://img.shields.io/pypi/v/local-abbfreeathome)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/local-abbfreeathome)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is a Python library that will interact with an ABB Free@Home SysAp over the Local API. For more information about the api, please visit the ABB [documentation](https://developer.eu.mybuildings.abb.com/fah_local).

**Note:** This is purely designed for the local api, these methods will not work when attempting to use the cloud api.

The primary motivation to building this library was to create a Home Assistant integration. Because of this the library will follow a lot of the same format and linting requirements as Home Assistant. Although this is designed with Home Assistant in mind, it's also designed as a completely independent library that can be used for any situation.

## Activate Local API

Using the local API will only work if you have it enabled on the SysAP. To activate the load API navigate to:

`SysAP Configuration` > `Settings` > `free@home - Settings` > `Local API` > `Activate Local API`

Copy the username listed within that window (usually `installer`) to be used when invoking the api.

## Channel Implementation

The current channels implemented within the library.
| Name | Primary Functions | Properties |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| BlindSensor | | `state`, `step_state`, `move_state` |
| BrightnessSensor | | `state`, `alarm` |
| CarbonMonoxideSensor | | `state` |
| ColorTemperatureActuator | `turn_on()`, `turn_off()`, `set_brightness()`, `set_forced_position()`, `set_color_temperature()` | `state`, `brightness`, `forced_position`, `color_temperature`, `color_temperature_coolest`, `color_temperature_warmest` |
| CoverActuator | `open()`,`close()`, `stop()`, `set_forced_position()`, `set_position()`, `set_tilt_position()` | `state`, `forced_position`, `position`, `tilt_position` |
| DesDoorOpenerActuator | `lock()`, `unlock()` | `state` |
| DesDoorRingingSensor | | |
| DimmingActuator | `turn_on()`, `turn_off()`, `set_brightness()`, `set_forced_position()` | `state`, `brightness`, `forced_position` |
| DimmingSensor\* | `turn_on_led()`, `turn_off_led()` | `state` |
| ForceOnOffSensor | | `state` |
| HeatingActuator | `set_position()` | `position` |
| MovementDetector | | `state`, `brightness` |
| RainSensor | | `state` |
| RoomTemperatureController | `turn_on()`, `turn_off()`, `eco_on()`, `eco_off()`, `set_temperature()` | `state`, `current_temperature`, `valve`, `target_temperature`, `state_indication`, `eco_mode` |
| SmokeDetector | | `state` |
| SwitchActuator | `turn_on()`, `turn_off()`, `set_forced_position()` | `state`, `forced_position` |
| SwitchSensor\* | `turn_on_led()`, `turn_off_led()` | `state` |
| TemperatureSensor | | `state`, `alarm` |
| Trigger | `press()` | |
| WindSensor | | `state`, `alarm`, `force` |
| WindowDoorSensor | | `state`, `position` |
| **Virtual Devices:** | | |
| BrightnessSensor | `turn_on()`, `turn_off()`, `set_brightness()` | `brightness`, `alarm` |
| EnergyBattery | `set_battery_power()`, `set_soc()`, `set_imported_today()`, `set_exported_today()`, `set_imported_total()`, `set_exported_total()` | `battery`, `soc`, `imported_today`, `exported_today`, `imported_total` `exported_total` |
| EnergyInverter | `set_current_power()`, `set_imported_today()`, `set_imported_total()` | `current_power`, `imported_today`, `imported_total` |
| EnergyTwoWayMeter | `set_current_power()`, `set_imported_today()`, `set_exported_today()`, `set_imported_total()`, `set_exported_total()` | `current_power`, `imported_today`, `exported_today`, `imported_total` `exported_total` |
| RainSensor | `turn_on()`, `turn_off()` | `alarm` |
| SwitchActuator | `turn_on()`, `turn_off()` | `state`, `requested_state` |
| TemperatureSensor | `turn_on()`, `turn_off()`, `set_temperature()` | `temperature`, `alarm` |
| WindSensor | `turn_on()`, `turn_off()`, `set_speed()`, `set_force()` | `speed`, `force`, `alarm` |
| WindowDoorSensor | `turn_on()`, `turn_off()` | `state` |

\*DimmingSensor and SwitchSensor: `turn_on_led()`and `turn_off_led()` refers to the LED of the sensor. It only has an effect when the "LED mode" is set to "Status Indication".

## FreeAtHome Class Structure and API Interaction

The general structure of the Python libary looks similar to this:

```
FreeAtHomeApi
│
└───FreeAtHome
     │
     └────Channels
          │  MovementDetector (FID_MOVEMENT_DETECTOR)
          │  SwitchActuator (FID_SWITCH_ACTUATOR)
          │  SwitchSensor (FID_SWITCH_SENSOR)
          │  Trigger (FID_TRIGGER)
```

The `FreeAtHome` class (in general) would NOT update the state of any individual channel (with the exception of the websocket callbacks). The channel class would have access to the FreeAtHome api object to update or fetch it's own state if needed. The `FreeAtHome` class's only interaction with the `FreeAtHomeApi` would be to fetch the SysAP configuration, which it will use to "load" the list of Python `channel` classes required for device interaction, and to listen for events on the websocket.

To make things simple and easy to test each channel should map to a single Free@Home [function](https://developer.eu.mybuildings.abb.com/fah_local/reference/functionids). This is because each function would likely have a unique set up inputs/outputs to interact with the Free@Home device, requiring unique methods within the class to properly expose and update the device. But, it is possible that a channel could have multiple functions if the functions operated identically to each other. This mapping can be applied in the `FreeAtHome._get_function_to_channel_mapping` method.

| Channel Class  | Function(s)         |
| -------------- | ------------------- |
| SwitchActuator | FID_SWITCH_ACTUATOR |

If multiple functions share a number of the same properties but are slightly different we can create additional levels to the class inheritence hierachy as needed to avoid repeat code.

### Channel Api Interaction (Update Channel)

Within the channel class any number of methods and functions can be implemented in order to both expose the information from the api as channel properties (e.g. lux, state) or set the state of a channel in Free@Home using the api object.

#### Set Channel Initial State

All channel states can be derived from the `inputs`, `outputs`, and `parameters` class attributes that will be available to all channel classes and is set in the `Base` channel class. The state of a channel is generally set using the channel `outputs`. An example if getting the current state of the SwitchActuator

```python
def _refresh_state_from_output(self, output: dict[str, Any]) -> bool:
    """
    Refresh the state of the device from a given output.

    This will return whether the state was refreshed as a boolean value.
    """
    if output.get("pairingID") == Pairing.AL_INFO_ON_OFF.value:
        self._state = output.get("value") == "1"
        return True
    return False
```

This is called when the channel class is initiated to know the current state of the channel. Because the `inputs`, `outputs`, and `parameters` are fed to the channel class from the `FreeAtHome` class, it does not need to interact directly with the api server. This is important, this ensures we don't have to invoke the Api every time we create an instance of a new channel class.

#### Refresh Channel State

There may be instances where the state of the channel would need to be refreshed directly from the api. In general, it's unlikely this will need to be called often, the updated state of a channel should come from the websocket and directed by the FreeAtHome with callbacks. But it's good practice to implement an api refresh.

To do this we can invoke the `FreeAtHomeApi.get_datapoint` function to fetch the state of the channel. We can use the `get_output_by_pairing_id` function to fetch the correct output id based on what is needed from the api.

```python
async def refresh_state(self):
    """Refresh the state of the channel from the api."""
    _state_refresh_pairings = [
        Pairing.AL_INFO_ON_OFF,
    ]

    for _pairing in _state_refresh_pairings:
        _switch_output_id, _switch_output_value = self.get_output_by_pairing(
            pairing=_pairing
        )

        _datapoint = (
            await self._api.get_datapoint(
                device_serial=self.device_serial,
                channel_id=self.channel_id,
                datapoint=_switch_output_id,
            )
        )[0]

        self._refresh_state_from_output(
            output={
                "pairingID": _pairing.value,
                "value": _datapoint,
            }
        )

@property
def state(self) -> bool | None:
    """Get the state of the switch."""
    return self._state
```

#### Update Channel State

To update the state (e.g. switch on channel) of a channel in the Free@Home system the api will need to be invoked. This is also done directly within the channel class.

This will use the `FreeAtHomeApi.set_datapoint` function using similar methods as fetching the state of the device.

```python
async def _set_switching_datapoint(self, value: str):
    _switch_input_id, _switch_input_value = self.get_input_by_pairing(
        pairing=Pairing.AL_SWITCH_ON_OFF
    )
    return await self._api.set_datapoint(
        device_serial=self.device_serial,
        channel_id=self.channel_id,
        datapoint=_switch_input_id,
        value=value,
    )

async def turn_on(self):
    """Turn on the switch."""
    await self._set_switching_datapoint("1")
    self._state = True
```

## Installation

Create a directory and virtual environment and install the Python library using pip.

```shell
mkdir -p ~/test_abbfreeathome && cd ~/test_abbfreeathome
python3.12 -m venv .venv && source ./.venv/bin/activate
pip install --upgrade local-abbfreeathome
```

Replace `python3.12` with your Python bash alias, double check which directory you want to install the virtual environment into.

Create any number of python files using the examples below (or your own code) to interact with the api.

## Development

The easiest way to develop is in Visual Studio and the use of DevContainers. It'll also ensure you're following the same code formatting and linting standards as everyone else. It'll also get your local environment setup with all the tools required in minutes.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Git](https://git-scm.com/)

### Getting Started

1. If you don't have access to this repository, start by forking the repo into your own account.
2. Open up Visual Studio Code, navigate to the [Command Palette](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette) and search for `Dev Containers: Clone Repository in Container Volume`.
3. You'll be prompted to enter the GitHub Repository URL. This will your forked repo url (unless you have access to this repo).
4. The dev container image will be built, once this is complete you'll be ready to develop!

### Tests

You can run a few tests to ensure everything is working as it should.

1. In Visual Studio Code, Navigate to the `Testing` tab on the left and click `Run Tests` (Double Play Icon). This should run all Python Unit Tests. You can also run `Run Tests With Coverage` to get the code coverage results.
2. In a new terminal window you can run `python3 -m build` to build and package up the python code.

## Examples

Below are a number of examples on how to use the library. These examples use the above directory and virtual environment.

## Api

There is one class which is designed to only interact with the api. This should be the only class that directory interacts with the api endpoints.

### Get Configuration

There's is one endpoint that'll return the entire Free@Home configuration, including all devices. This example shows how to fetch and display that. Keep in mind the devices returned are are just Python `dict` objects.

```python
from abbfreeathome import FreeAtHomeApi
import asyncio
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Create an instance of the free@home api
    _fah_api = FreeAtHomeApi(
        host="http://<IP or HOSTNAME>", username="installer", password="<password>"
    )

    # Pull SysAP Configuration
    _config = asyncio.run(_fah_api.get_configuration())

    # Print All Devices
    print(_config.get("devices"))
```

## FreeAtHome

There an additional class called `FreeAtHome`. This class attempts to put it all together linking the `FreeAtHomeApi` class to usable Python objects.

### Get Channels

This example will load the `FreeAtHome` class with all potential channels from the api. Once loaded another function `get_channels_by_class` is used to pull all channels that fall under a specific "class".

```python
from abbfreeathome import FreeAtHome, FreeAtHomeApi
from abbfreeathome.channels.switch_actuator import SwitchActuator
import logging
import asyncio

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Create an instance of the FreeAtHome class.
    _free_at_home = FreeAtHome(
        api=FreeAtHomeApi(
          host="http://<IP or HOSTNAME>", username="installer", password="<password>"
        )
    )

    # Load all channels into the FreeAtHome object.
    asyncio.run(_free_at_home.load())

    # Fetch just the list of switches
    _switches = _free_at_home.get_channels_by_class(channel_class=SwitchActuator)

    # Loop through each switch showing the name and whether is On/Off
    for _switch in _switches:
        print(_switch.channel_name, f"({_switch.state})")
```

### WebSocket

The Free@Home local api also exposes a websocket. With this library you can connect to and listen to events on the websocket. These events are changes in channels datapoints, parameters, etc. The library will give the ability to listen on the websocket and automatically update a channel's state.

In addition, the library "channels" can register and run any callbacks when the state changes. Allowing outside code (e.g. Home Assistant) to get notified on changes.

```python
from abbfreeathome import FreeAtHome, FreeAtHomeApi
from abbfreeathome.channels.switch_actuator import SwitchActuator
import logging
import asyncio


async def websocket_test():
    # Create an instance of the api using context management
    async with FreeAtHomeApi(
        host="http://<IP or HOSTNAME>", username="installer", password="<password>"
    ) as _free_at_home_api:
        # Create an Instance of the FreeAtHome class
        _free_at_home = FreeAtHome(_free_at_home_api)

        # Load all channels into the FreeAtHome Class
        await _free_at_home.load()

        # Add our very own callback
        for _switch in _free_at_home.get_channels_by_class(channel_class=SwitchActuator):
            _switch.register_callback(
                callback_attribute="state", callback=my_very_own_callback
            )

        # Start listening for events.
        await _free_at_home.ws_listen()


def my_very_own_callback():
    print("The switches datapoints have been updated.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(websocket_test())
```

#### Output

In order to see any activity, you'll have to turn on/off a switch in the system.

```
INFO:abbfreeathome.api:Websocket attempting to connect ws://<IP or HOSTNAME>/fhapi/v1/api/ws
INFO:abbfreeathome.api:Websocket connected ws://<IP or HOSTNAME>/fhapi/v1/api/ws
INFO:abbfreeathome.channels.base:Office Light received updated data: ABB7F62F6C25/ch0003/idp0000: 1
The switches datapoints have been updated.
INFO:abbfreeathome.channels.base:Office Light received updated data: ABB7F62F6C25/ch0003/odp0000: 1
The switches datapoints have been updated.
```

### Devices / Free@Home Overview

Here is example code that'll output all of the devices in your Free@Home setup. Including some general information about the setup (e.g. number of devices, unresponsive devices, counts by interfact)

```python
import asyncio

from abbfreeathome import FreeAtHome, FreeAtHomeApi
from abbfreeathome.bin.interface import Interface


async def main():
    # Create an instance of the FreeAtHome class.
    _free_at_home = FreeAtHome(
        api=FreeAtHomeApi(
          host="http://<IP or HOSTNAME>", username="installer", password="<password>"
        )
    )

    # Load devices and channels
    await _free_at_home.load()

    # Get all devices
    _devices = _free_at_home.get_devices()

    # Iterate through devices
    for _device in _devices.values():
        print(str(_device))

    # Number of devices
    print(f"\nFound {len(_devices)} devices")

    # Unresponsive devices
    _unresponsive_devices = [
        device for device in _devices.values() if device.unresponsive
    ]
    print(f"Unresponsive devices: {len(_unresponsive_devices)}\n")

    # Filter devices by interface using the Interface enum
    # Devices by interface
    for _interface in Interface:
        _device_by_interface = [
            _device for _device in _devices.values() if _device.interface == _interface
        ]
        print(f"{_interface} devices: {len(_device_by_interface)}")

    # Close api session
    await _free_at_home.api.close_client_session()


if __name__ == "__main__":
    asyncio.run(main())
```

## TODO

There are a number of items that still need to be done.

- ~~Implement format and linting checking in a GitHub actions pipeline using Ruff.~~
  - ~~https://docs.astral.sh/ruff/integrations/~~
- ~~Add GitHub actions for cutting a release and pushing to PyPi automatically.~~
- ~~Implement unit testing.~~
- Implement SSL on both HTTPS and WSS requests.
  - The Free@Home system will provide a certificate which can be used to validate the connection, can this be used in Home Assistant?
