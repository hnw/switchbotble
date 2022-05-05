#!/usr/bin/env python3
import asyncio
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

async def main():
    ble = SwitchBotBLE()
    ble.subscribe(allCatchListener)
    while True:
        async with ble:
            await asyncio.sleep(7.0)

asyncio.run(main())
