from abc import ABCMeta, abstractmethod
from bleak.backends.scanner import BLEDevice
from datetime import datetime as dt
from blinker import signal

class SwitchBotDevice(metaclass=ABCMeta):
    def __init__(self, d: BLEDevice, service_data: bytearray):
        self.debug = False
        self.d = d
        self.prev = None
        self._map_fields(d, service_data)
        self.publish("found")

    def update(self, d: BLEDevice, service_data: bytearray):
        self.d = d
        self.prev = self.__dict__.copy()
        self._map_fields(d, service_data)
        self._check_diff()

    def publish(self, topicName: str):
        sig = signal(topicName)
        sig.send(f"{self.d.address}", device=self, signal=sig)

    @staticmethod
    def subscribe(listener, address: str = None, topicName: str = None):
        if address == None:
            topicName = pub.ALL_TOPICS
        elif topicName == None:
            topicName = f"{address}"
        else:
            topicName = f"{address}.{topicName}"

    @abstractmethod
    def _map_fields(self, d: BLEDevice, service_data: bytearray):
        pass

    @abstractmethod
    def _check_diff(self):
        pass

    def log(self, message: str):
        if self.debug:
            print(f"{dt.now().isoformat()} {self.d.address} {message}")
