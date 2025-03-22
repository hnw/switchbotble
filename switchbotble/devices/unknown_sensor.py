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

    def _check_status(self, curr):
        prev = self.status
        if prev['manufacturer_data'] != curr['manufacturer_data']:
            self.log(f"manufacturer_data: {prev['manufacturer_data']} -> {curr['manufacturer_data']}")
        if prev['service_data'] != curr['service_data']:
            self.log(f"service_data: {prev['service_data']} -> {curr['service_data']}")

    def __str__(self):
        return f"{self.__class__.__name__}: battery={self.battery}, light={self.light}, motion_raw={self.motion_raw}, motion={self.motion}, last_motion={self.last_motion}, contact={self.contact}, hal_utc={self.last_contact}, enter_count={self.enter_count}, exit_count={self.exit_count}, button_count={self.button_count}"
