from bleak.backends.scanner import BLEDevice, AdvertisementData
from .base import SwitchBotDevice

class WaterLeakDetector(SwitchBotDevice):
    def __init__(self, d: BLEDevice, **kwargs):
        super().__init__(d, **kwargs)

    def _parse_advertisement_data(self, ad: AdvertisementData):
        data = bytearray(next(iter(ad.manufacturer_data.values())))
        # 0-5: \xcf 4 0 7 q U
        # 6:\x0e
        # 7:d
        # \x9c \x00 \x00 \x00 \n < \x05 \x00 $ \xe8 \x1e'), 'service_data': bytearray(b'&\x00d')}
        return {
            # RSSI
            'rssi': ad.rssi,
            # MAC Address
            'mac_address': ':'.join(f"{byte:02X}" for byte in data[:6]),
            # sequence number
            'sequence_number': data[6],
            # Battery
            'battery': data[7] & 0x7f,
            # other
            '8': data[8],
            '9': data[9],
            '10': data[10],
            '11': data[11],
            '12': data[12],
            '13': data[13],
            '14': data[14],
            '15': data[15],
            '16': data[16],
            '17': data[17],
            '18': data[18],
        }

    def _check_status(self, curr):
        prev = self.status
        self.log(f"{curr}")

    def __str__(self):
        return f"{self.__class__.__name__}: battery={self.battery}, light={self.light}, motion_raw={self.motion_raw}, motion={self.motion}, last_motion={self.last_motion}, contact={self.contact}, hal_utc={self.last_contact}, enter_count={self.enter_count}, exit_count={self.exit_count}, button_count={self.button_count}"
