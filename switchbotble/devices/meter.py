from bleak.backends.scanner import BLEDevice, AdvertisementData
from .base import SwitchBotDevice

class Meter(SwitchBotDevice):
    def __init__(self, d: BLEDevice, **kwargs):
        super().__init__(d, **kwargs)

    def _parse_advertisement_data(self, ad: AdvertisementData):
        data = bytearray(next(iter(ad.service_data.values())))
        return {
            # RSSI
            'rssi': ad.rssi,
            # Battery
            'battery': data[2] & 0x7f,
            # Temperature
            'temperature': ((data[3] & 0x0f) * 0.1 + (data[4] & 0x7f)) * (1 if (data[4] & 0x80) > 0 else -1),
            'temperature_alert': (data[3] & 0xc0) >> 6,
            # Humidity
            'humidity' : data[5] & 0x7f,
            'humidity_alert': (data[3] & 0x30) >> 4,
        }

    def _publish_signal(self):
        pass
