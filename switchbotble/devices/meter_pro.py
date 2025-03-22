from bleak.backends.scanner import BLEDevice, AdvertisementData
from .base import SwitchBotDevice

class MeterPro(SwitchBotDevice):
    def __init__(self, d: BLEDevice, **kwargs):
        super().__init__(d, **kwargs)

    def _parse_advertisement_data(self, ad: AdvertisementData):
        data = bytearray(next(iter(ad.manufacturer_data.values())))
        status = {
            # RSSI
            'rssi': ad.rssi,
            # MAC Address
            #'mac_address': ':'.join(f"{byte:02X}" for byte in data[:6]),
            # sequence number
            #'sequence_number': data[6],
            # Battery
            'battery': data[7] & 0x7f,
            'usb_charging': bool(data[7] & 0x80),
            # Temperature
            'temperature': ((data[8] & 0x0f) * 0.1 + (data[9] & 0x7f)) * (1 if (data[9] & 0x80) > 0 else -1),
            'temperature_alert': (data[8] & 0xc0) >> 6,
            # Humidity
            'humidity' : data[10] & 0x7f,
            'humidity_alert': (data[8] & 0x30) >> 4,
            'comfort_level': data[11] & 0x03, # 0:comfort, 1:dry, 2:wet
        }
        if (len(data) >= 16):
            # Meter Pro (CO2 Monitor)
            status['co2'] = data[13] * 256 + data[14]
            status['co2_level'] = (data[15] & 0x60) >> 5 # 0:good, 1:average, 2:poor
        return status

    def _publish_signal(self):
        pass
