#!/usr/bin/env python3
import subprocess
import platform
import asyncio
from switchbotble import SwitchBotBLE, motion, no_motion, closed

# uses 48bit MAC address on Windows/Linux
kitchen = '00:00:5E:00:53:C7' # MAC address for motion sensor
bedroom = '00:00:5E:00:53:22' # MAC address for contact sensor
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
