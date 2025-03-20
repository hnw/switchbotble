from abc import ABCMeta, abstractmethod
from bleak.backends.scanner import BLEDevice, AdvertisementData
from datetime import datetime as dt
from blinker import signal

class SwitchBotDevice(metaclass=ABCMeta):
    def __init__(self, d: BLEDevice, debug = False, **kwargs):
        self.debug = debug
        self.d = d
        self.prev_status = None
        self.status = None

    def update(self, ad: AdvertisementData):
        status = self._parse_advertisement_data(ad)
        if self.status == status:
            return
        self.prev_status = self.status
        self.status = status
        self._process_status()
        if self.prev_status == None:
            self.publish("found")
        else:
            self._publish_signal()

    def publish(self, topic_name: str):
        sig = signal(topic_name)
        sig.send(f"{self.d.address}", device=self, signal=sig)

    @abstractmethod
    def _parse_advertisement_data(self, ad: AdvertisementData):
        pass

    def _process_status(self):
        pass

    def _publish_signal(self):
        pass

    def log(self, message: str):
        if self.debug:
            print(f"{dt.now().isoformat()} {self.d.address} {message}")

    def __str__(self):
        if self.status:
            status_str = ", ".join(f"{key}={value}" for key, value in self.status.items())
            return f"{self.__class__.__name__}: {status_str}"
        else:
            return f"{self.__class__.__name__}: Status is None"
