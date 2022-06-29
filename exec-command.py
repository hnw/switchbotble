#!/usr/bin/env python3
import os,sys
import asyncio
import subprocess
from datetime import datetime as dt
from switchbotble import SwitchBotBLE
from blinker import signal

found       = signal('found')
motion      = signal('motion')
motion_l    = signal('motion_l')
no_motion   = signal('no_motion')
no_motion_l = signal('no_motion_l')
opened      = signal('opened')
closed      = signal('closed')
pushed      = signal('pushed')

kitchen = '00:00:5E:00:53:C7'
bedroom1 = '00:00:5E:00:53:22'
bedroom2 = '00:00:5E:00:53:E2'

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

@motion_l.connect_via(kitchen)
def kitchen_on(address, **kw):
    subprocess.Popen(['/home/pi/bin/g', 'キッチンのデバイスをつけて'])

@no_motion_l.connect_via(kitchen)
def kitchen_off(address, **kw):
    subprocess.Popen(['/home/pi/bin/g', 'キッチンのデバイスを消して'])

@motion_l.connect_via(bedroom1)
def bedroom_on(address, **kw):
    if kw['device'].opened:
        subprocess.Popen(['/home/pi/bin/g', '寝室のデバイスをつけて'])

@no_motion_l.connect_via(bedroom1)
def bedroom_off(address, **kw):
    subprocess.Popen(['/home/pi/bin/g', '寝室のデバイスを消して'])

@pushed.connect_via(bedroom2)
def floorlamp_on_off(address, **kw):
    if kw['device'].light:
        subprocess.Popen(['/home/pi/bin/g', '寝室のデバイスを消して'])
    else:
        subprocess.Popen(['/home/pi/bin/g', 'フロアランプをつけて'])

@closed.connect_via(bedroom1)
def all_off(address, **kw):
    subprocess.Popen(['/home/pi/bin/g', '全部のデバイスを消して'])

async def main():
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
    ble = SwitchBotBLE()

    while True:
        await ble.start()
        await asyncio.sleep(2.0)
        await ble.stop()

asyncio.run(main())
