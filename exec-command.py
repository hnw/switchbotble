#!/usr/bin/env python3
import asyncio
import subprocess
from datetime import datetime as dt
from switchbotble import SwitchBotBLE
from pubsub import pub

def allCatchListener(topicObj = pub.AUTO_TOPIC, **msgData):
    device = msgData['arg1']
    address,topicName = topicObj.getName().split('.')
    message = ""
    if topicName == "motion" or  topicName == "no_motion" or topicName == "motion_l" or  topicName == "no_motion_l":
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
    subprocess.run(['/home/pi/bin/g', 'キッチンのデバイスをつけて'])

def kitchen_off(arg1):
    subprocess.run(['/home/pi/bin/g', 'キッチンのデバイスを消して'])

def bedroom_on(arg1):
    if arg1.open:
        subprocess.run(['/home/pi/bin/g', '寝室のデバイスをつけて'])

def bedroom_off(arg1):
    subprocess.run(['/home/pi/bin/g', '寝室のデバイスを消して'])

def all_off(arg1):
    subprocess.run(['/home/pi/bin/g', '全部のデバイスを消して'])

async def main():
    ble = SwitchBotBLE()
    kitchen_address = '00:00:5E:00:53:C7'
    bedroom_address = '00:00:5E:00:53:22'
    ble.subscribe(allCatchListener)
    ble.subscribe(kitchen_init, kitchen_address, 'connected')
    ble.subscribe(kitchen_on, kitchen_address, 'motion_l')
    ble.subscribe(kitchen_off, kitchen_address, 'no_motion_l')
    ble.subscribe(bedroom_init, bedroom_address, 'connected')
    ble.subscribe(bedroom_on, bedroom_address, 'motion_l')
    ble.subscribe(bedroom_off, bedroom_address, 'no_motion_l')
    ble.subscribe(all_off, bedroom_address, 'closed')

    while True:
        async with ble:
            await asyncio.sleep(3.0)

asyncio.run(main())
