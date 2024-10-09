# Python Package - ABB Free@Home via Local Api

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

## Device Implementation

The current devices implemented within the library.

| Name | Primary Functions |
|--|--|
| SwitchActuator | `turn_on()`, `turn_off()` |

## Installation

Create a directory and virtual environment and install the Python library using pip.

```shell
mkdir -p ~/test_abbfreeathome && cd ~/test_abbfreeathome
python3.12 -m venv .venv && source ./.venv/bin/activate
pip install --upgrade local-abbfreeathome
```

Replace `python3.12` with your Python bash alias, double check which directory you want to install the virtual environment into.

Create any number of python files using the examples below (or your own code) to interact with the api.

## Examples

Below are a number of examples on how to use the library. These examples use the above directory and virtual environment.

## Api

There is one class which is designed to only interact with the api. This should be the only class that directory interacts with the api endpoints.

### Get Configuration

There's is one endpoint that'll return the entire Free@Home configuration, including all devices. This example shows how to fetch and display that. Keep in mind the devices returned are are just Python `dict` objects.

```python
from abbfreeathome.api import FreeAtHomeApi
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

### Get Devices

This example will load the `FreeAtHome` class with all potential devices from the api. Once loaded another function `get_device_by_class` is used to pull all devices that call under a specific "class".

```python
from abbfreeathome.api import FreeAtHomeApi
from abbfreeathome.freeathome import FreeAtHome
from abbfreeathome.devices.switch_actuator import SwitchActuator
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

    # Load all devices into the FreeAtHome object.
    asyncio.run(_free_at_home.load_devices())

    # Fetch just the list of switches
    _switches = _free_at_home.get_device_by_class(device_class=SwitchActuator)

    # Loop through each switch showing the name and whether is On/Off
    for _switch in _switches:
        print(_switch.channel_name, f"({_switch.state})")
```

### WebSocket

The Free@Home local api also exposes a websocket. With this library you can connect to and lisen to events on the websocket. These events are changes in devices datapoints, parameters, etc. The library will give the ability to listen on the websocket and automatically update a devices state.

In addition, the library "devices" can register and run any callbacks when the state changes. Allowing outside code (e.g. Home Assistant) to get notified on changes.

```python
from abbfreeathome.api import FreeAtHomeApi
from abbfreeathome.freeathome import FreeAtHome
from abbfreeathome.devices.switch_actuator import SwitchActuator
import logging
import asyncio


def my_very_own_callback():
    print("The switches datapoints have been updated.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    _free_at_home = FreeAtHome(
        api=FreeAtHomeApi(
          host="http://<IP or HOSTNAME>", username="installer", password="<password>"
        )
    )

    # Load all devices into the FreeAtHome object.
    asyncio.run(_free_at_home.load_devices())

    # Set the callback function on each switch.
    for _switch in _free_at_home.get_device_by_class(device_class=SwitchActuator):
        _switch.register_callback(my_very_own_callback)

    # Start listenting
    asyncio.run(_free_at_home.ws_listen())
```

#### Output

In order to see any activity, you'll have you turn on/off a switch in the system.

```
INFO:abbfreeathome.api:Websocket attempting to connect ws://<IP or HOSTNAME>/fhapi/v1/api/ws
INFO:abbfreeathome.api:Websocket connected ws://<IP or HOSTNAME>/fhapi/v1/api/ws
INFO:abbfreeathome.devices.switch:Office Light received updated data: ABB7F62F6C25/ch0003/idp0000: 1
The switches datapoints have been updated.
INFO:abbfreeathome.devices.switch:Office Light received updated data: ABB7F62F6C25/ch0003/odp0000: 1
The switches datapoints have been updated.
```

## TODO

There are a number of items that still need to be done.

- ~~Implement format and linting checking in a GitHub actions pipeline using Ruff.~~
  - ~~https://docs.astral.sh/ruff/integrations/~~
- ~~Add GitHub actions for cutting a release and pushing to PyPi automatically.~~
- ~~Implement unit testing.~~
- Implement SSL on both HTTPS and WSS requests.
  - The Free@Home system will provide a certificate which can be used to validate the connection, can this be used in Home Assistant?
