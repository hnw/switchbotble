from abc import ABCMeta, abstractmethod
from bleak.backends.scanner import BLEDevice, AdvertisementData
from .base import SwitchBotDevice
from .contact_sensor import ContactSensor
from .motion_sensor import MotionSensor
from .unknown_sensor import UnknownSensor

class SwitchBotDeviceFactory(metaclass=ABCMeta):
    @staticmethod
    def create(dev_type: int, d: BLEDevice, **kwargs) -> SwitchBotDevice:
        # see: https://github.com/OpenWonderLabs/SwitchBotAPI-BLE#device-types
        if dev_type == 0x64:
            return ContactSensor(d, **kwargs)
        elif dev_type == 0x73:
            return MotionSensor(d, **kwargs)
        else:
            if kwargs.get("debug"):
                print(f"Unknown device type '{chr(dev_type)}'({hex(dev_type)})")
            return UnknownSensor(d, **kwargs)
