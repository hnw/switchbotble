from abc import ABCMeta, abstractmethod
from bleak.backends.scanner import BLEDevice, AdvertisementData
from datetime import datetime as dt
from blinker import signal

class SwitchBotDevice(metaclass=ABCMeta):
    def __init__(self, d: BLEDevice, debug = False, **kwargs):
        self.debug = debug
        self.d = d
        self.status = None

    def update(self, ad: AdvertisementData):
        current_status = self._parse_advertisement_data(ad)
        if self.status == None:
            self.status = current_status
            self.publish("found")
        else:
            self._check_status(current_status)
            self.status = current_status

    def publish(self, topic_name: str):
        sig = signal(topic_name)
        sig.send(f"{self.d.address}", device=self, signal=sig)

    @abstractmethod
    def _parse_advertisement_data(self, ad: AdvertisementData):
        pass

    @abstractmethod
    def _check_status(self, curr):
        pass

    def log(self, message: str):
        if self.debug:
            print(f"{dt.now().isoformat()} {self.d.address} {message}")
