Switchbotble is an event-driven SwitchBot sensor library using BLE written in Python.

## Installation

```
$ pip install switchbotble
```

## Features

* Scans all nearby SwitchBot devices with BLE, and publishes events if the sensor value changed.
* Supports BLE on Windows 10, Linux, OS X/macOS (provided by BLE library [Bleak](https://github.com/hbldh/bleak))
* Supporting Switchbot sensors:
  * Contact sensor
  * Motion sensor
* Supporting sensor events:
  * Movement detection (Contact sensor, Motion sensor)
  * Light detection (Contact sensor, Motion sensor)
  * Door open/close detection (Contact sensor)
  * Button press detection (Contact sensor)

## Usage

``` python
import subprocess
import platform
import asyncio
from switchbotble import SwitchBotBLE, motion, no_motion, closed

# uses 48bit MAC address on Windows/Linux
kitchen = '00:00:5E:00:53:C7' # Mac Address for motion sensor
bedroom = '00:00:5E:00:53:22' # Mac Address for contact sensor
if platform.system() == "Darwin":
    # uses 128bit UUID on MacOS
    kitchen = 'ECFAB3FC-FAE2-11EC-A7F7-00005E0053C7'
    bedroom = 'ECFAB3FC-FAE2-11EC-A7F7-00005E005322'

@motion.connect_via(kitchen)
def kitchen_on(address, **kwargs):
    subprocess.Popen(['google', 'Turn on all lights in kitchen'])

@no_motion.connect_via(kitchen)
def kitchen_off(address, **kwargs):
    subprocess.Popen(['google', 'Turn off all lights in kitchen'])

@closed.connect_via(bedroom)
def all_off(address, **kwargs):
    subprocess.Popen(['google', 'Turn off all devices'])

async def main():
    ble = SwitchBotBLE(motion_timeout = 180)
    while True:
        await ble.start()
        await asyncio.sleep(2.0)
        await ble.stop()

asyncio.run(main())
```
