#!/usr/bin/env python3
import asyncio
from datetime import datetime as dt
from switchbotble import SwitchBotBLE
from blinker import ANY, signal

found       = signal('found')
motion      = signal('motion')
motion_l    = signal('motion_l')
no_motion   = signal('no_motion')
no_motion_l = signal('no_motion_l')
opened      = signal('opened')
closed      = signal('closed')
pushed      = signal('pushed')

@found.connect
@motion.connect
@motion_l.connect
@no_motion.connect
@no_motion_l.connect
@opened.connect
@closed.connect
@pushed.connect
def allCatchListener(address, **kw):
    device = kw['device']
    signal = kw['signal']
    message = ""
    if signal == found:
        message = f": rssi = {device.d.rssi}dBm"
    elif signal == motion or  signal == no_motion or signal == motion_l or  signal == no_motion_l:
        message = f": last_motion = {device.last_motion}"
    elif signal == opened or  signal == closed:
        message = f": contact = {device.contact}, last_contact = {device.last_contact}"
    elif signal == pushed:
        message = f": push_count = {device.push_count}"
    print(f"{dt.now().isoformat()} {address} {signal.name} {message}")

async def main():
    ble = SwitchBotBLE()
    while True:
        async with ble:
            await asyncio.sleep(7.0)

asyncio.run(main())
