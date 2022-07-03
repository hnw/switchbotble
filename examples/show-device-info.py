#!/usr/bin/env python3
import asyncio
from datetime import datetime as dt
from switchbotble import SwitchBotBLE, found, motion, no_motion, light, dark, opened, closed, entered, exited, pushed

@found.connect
@motion.connect
@no_motion.connect
@light.connect
@dark.connect
@opened.connect
@closed.connect
@entered.connect
@exited.connect
@pushed.connect
def allCatchListener(address, device, signal, **kwargs):
    message = ""
    if signal == found:
        message = f": rssi = {device.d.rssi}dBm"
    elif signal == motion or  signal == no_motion:
        message = f": last_motion = {device.last_motion}"
    elif signal == opened or  signal == closed:
        message = f": contact = {device.contact}, last_contact = {device.last_contact}"
    elif signal == pushed:
        message = f": push_count = {device.push_count}"
    print(f"{dt.now().isoformat()} {address} {signal.name} {message}")

async def main():
    ble = SwitchBotBLE(motion_timeout = 60)
    while True:
        async with ble:
            await asyncio.sleep(7.0)

asyncio.run(main())
