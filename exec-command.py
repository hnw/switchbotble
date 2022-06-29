#!/usr/bin/env python3
import os,sys
import asyncio
import subprocess
from datetime import datetime as dt
from switchbotble import SwitchBotBLE
from pubsub import pub

def allCatchListener(topicObj = pub.AUTO_TOPIC, **msgData):
    device = msgData['arg1']
    address,topicName = topicObj.getName().split('.')
    message = ""
    if topicName == "connected":
        message = f": rssi = {device.d.rssi}dBm"
    elif topicName == "motion" or  topicName == "no_motion" or topicName == "motion_l" or  topicName == "no_motion_l":
        message = f": last_motion = {device.last_motion}"
    elif topicName == "open" or  topicName == "closed":
        message = f": contact = {device.contact}, last_contact = {device.last_contact}"
    elif topicName == "pushed":
        message = f": push_count = {device.push_count}"
    print(f"{dt.now().isoformat()} {address} {topicName} {message}")

def kitchen_init(arg1):
    pass

def bedroom_init(arg1):
    arg1.debug = True

def kitchen_on(arg1):
    subprocess.Popen(['/home/pi/bin/g', 'キッチンのデバイスをつけて'])

def kitchen_off(arg1):
    subprocess.Popen(['/home/pi/bin/g', 'キッチンのデバイスを消して'])

def bedroom_on(arg1):
    if arg1.open:
        subprocess.Popen(['/home/pi/bin/g', '寝室のデバイスをつけて'])

def bedroom_off(arg1):
    subprocess.Popen(['/home/pi/bin/g', '寝室のデバイスを消して'])

def floorlamp_on_off(arg1):
    if arg1.light:
        subprocess.Popen(['/home/pi/bin/g', '寝室のデバイスを消して'])
    else:
        subprocess.Popen(['/home/pi/bin/g', 'フロアランプをつけて'])

def all_off(arg1):
    subprocess.Popen(['/home/pi/bin/g', '全部のデバイスを消して'])

async def main():
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
    ble = SwitchBotBLE()
    kitchen_addr = '00:00:5E:00:53:C7'
    bedroom1_addr = '00:00:5E:00:53:22'
    bedroom2_addr = '00:00:5E:00:53:E2'
    ble.subscribe(allCatchListener)
    ble.subscribe(kitchen_init, kitchen_addr, 'connected')
    ble.subscribe(kitchen_on, kitchen_addr, 'motion_l')
    ble.subscribe(kitchen_off, kitchen_addr, 'no_motion_l')
    ble.subscribe(bedroom_init, bedroom1_addr, 'connected')
    ble.subscribe(bedroom_on, bedroom1_addr, 'motion_l')
    ble.subscribe(bedroom_off, bedroom1_addr, 'no_motion_l')
    ble.subscribe(all_off, bedroom1_addr, 'closed')
    ble.subscribe(floorlamp_on_off, bedroom2_addr, 'pushed')

    while True:
        await ble.start()
        await asyncio.sleep(2.0)
        await ble.stop()

asyncio.run(main())
