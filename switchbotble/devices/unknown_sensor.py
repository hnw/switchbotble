from bleak.backends.scanner import BLEDevice, AdvertisementData
from .base import SwitchBotDevice

class UnknownSensor(SwitchBotDevice):
    def __init__(self, d: BLEDevice, **kwargs):
        super().__init__(d, **kwargs)

    def _parse_advertisement_data(self, ad: AdvertisementData):
        manufacturer_data = bytearray(next(iter(ad.manufacturer_data.values())))
        service_data = bytearray(next(iter(ad.service_data.values())))
        return {
            'rssi': ad.rssi,
            'manufacturer_data': manufacturer_data,
            'service_data': service_data,
        }

    def _process_status(self):
        if self.prev_status != None:
            if self.prev_status['manufacturer_data'] != self.status['manufacturer_data']:
                self.log(f"manufacturer_data: {self.prev_status['manufacturer_data']} -> {self.status['manufacturer_data']}")
            if self.prev_status['service_data'] != self.status['service_data']:
                self.log(f"service_data: {self.prev_status['service_data']} -> {self.status['service_data']}")
