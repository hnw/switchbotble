from abc import ABCMeta, abstractmethod
from bleak.backends.scanner import BLEDevice, AdvertisementData
from .base import SwitchBotDevice
from .contact_sensor import ContactSensor
from .motion_sensor import MotionSensor
from .meter import Meter
from .meter_pro import MeterPro
from .water_leak_detector import WaterLeakDetector
from .unknown_sensor import UnknownSensor

class DeviceType(Enum):
    # see: https://github.com/OpenWonderLabs/SwitchBotAPI-BLE#device-types
    CONTACT_SENSOR = 0x64
    MOTION_SENSOR = 0x73
    METER = 0x54
    METER_PRO = 0x35
    WATER_LEAK_DETECTOR = 0x26

class SwitchBotDeviceFactory(metaclass=ABCMeta):
    @staticmethod
    def create(dev_type: int, d: BLEDevice, **kwargs) -> SwitchBotDevice:
        # see: https://github.com/OpenWonderLabs/SwitchBotAPI-BLE#device-types
        if device_type == DeviceType.CONTACT_SENSOR:
            return ContactSensor(d, **kwargs)
        elif device_type == DeviceType.MOTION_SENSOR:
            return MotionSensor(d, **kwargs)
        elif device_type == DeviceType.METER:
            return Meter(d, **kwargs)
        elif device_type == DeviceType.METER_PRO:
            return MeterPro(d, **kwargs)
        elif device_type == DeviceType.WATER_LEAK_DETECTOR:
            return WaterLeakDetector(d, **kwargs)
        else:
            if kwargs.get("debug"):
                print(f"Unknown device type '{chr(dev_type)}'({hex(dev_type)})")
            return UnknownSensor(d, **kwargs)
