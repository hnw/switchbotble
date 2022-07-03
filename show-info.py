#!/usr/bin/env python3
import asyncio
from datetime import datetime as dt
from switchbotble import SwitchBotBLE
from blinker import ANY, signal

found       = signal('found')
motion      = signal('motion')
no_motion   = signal('no_motion')
opened      = signal('opened')
closed      = signal('closed')
pushed      = signal('pushed')

@found.connect
@motion.connect
@no_motion.connect
@opened.connect
@closed.connect
@pushed.connect
def allCatchListener(address, **kw):
    device = kw['device']
    signal = kw['signal']
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
