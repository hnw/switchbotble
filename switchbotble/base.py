import asyncio
from typing import List
from bleak import BleakScanner
from bleak.backends.scanner import BLEDevice, AdvertisementData
from .devices.base import SwitchBotDevice
from .devices.factory import SwitchBotDeviceFactory as factory
from blinker import signal

found     = signal('found')
motion    = signal('motion')
no_motion = signal('no_motion')
light     = signal('light')
dark      = signal('dark')
opened    = signal('opened')
closed    = signal('closed')
entered   = signal('entered')
exited    = signal('exited')
pushed    = signal('pushed')

class SwitchBotBLE(BleakScanner):
    # Company IDs for SwitchBot
    #   https://github.com/OpenWonderLabs/SwitchBotAPI-BLE
    #   https://www.bluetooth.com/ja-jp/specifications/assigned-numbers/company-identifiers/
    __company_id = [ 0x0059, 0x0969 ]

    # UUIDs for SwitchBot
    #   https://github.com/OpenWonderLabs/SwitchBotAPI-BLE
    #   https://www.bluetooth.com/specifications/assigned-numbers/ "16-bit UUIDs"
    # 0xfd3d : Woan Technology (Shenzhen) Co., Ltd.
    # 0x0d00 : old Service UUID
    __uuid = ["00000d00-0000-1000-8000-00805f9b34fb",
              "0000fd3d-0000-1000-8000-00805f9b34fb"]

    def __init__(self, **kwargs):
        super().__init__(detection_callback=self.__detection_callback)
        self.__switchbot_devices = {}
        self.__kwargs = kwargs

    def __detection_callback(self, d: BLEDevice, ad: AdvertisementData) -> None:
        if len(ad.manufacturer_data) != 1:
            return
        if len(ad.service_data) != 1:
            return
        company_id = next(iter(ad.manufacturer_data.keys()))
        uuid = next(iter(ad.service_data.keys()))
        if not company_id in self.__company_id:
            return
        if not uuid in self.__uuid:
            return
        device = self.__switchbot_devices.get(d.address)
        if device == None:
            service_data = ad.service_data[uuid]
            dev_type = bytearray(service_data)[0]
            device = factory.create(dev_type, d, **self.__kwargs)
            self.__switchbot_devices[d.address] = device
        device.update(ad)
