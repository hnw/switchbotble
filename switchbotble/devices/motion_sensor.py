from bleak.backends.scanner import BLEDevice, AdvertisementData
from .base import SwitchBotDevice

# see: https://github.com/OpenWonderLabs/python-host/wiki/Motion-Sensor-BLE-open-API
# PIR = Passive infrared(IR) sensor, motion sensor

class MotionSensor(SwitchBotDevice):
    def __init__(self, d: BLEDevice, **kwargs):
        self.motion_timeout_limit = 0
        self.motion_timeout = kwargs.get('motion_timeout', 30)
        self.ignore_motion_timeout = False
        super().__init__(d, **kwargs)

    def clear_current_motion_timeout(self):
        if self.motion:
            self.ignore_motion_timeout = True

    def _parse_advertisement_data(self, ad: AdvertisementData):
        service_data = bytearray(next(iter(ad.service_data.values())))
        curr = {
            'rssi': ad.rssi,
            # Battery value
            'battery': service_data[2] & 0x7f,
            # Light state
            'light': bool(service_data[5] & 0x02),
            # PIR state
            'motion_raw': bool(service_data[1] & 0x40),
            'last_motion': service_data[4] + service_data[3]*256 + ((service_data[5] & 0x80) >> 7)*65536,
            'motion' : bool(service_data[1] & 0x40),
        }
        if curr['motion'] == False and curr['last_motion'] < self.motion_timeout_limit:
            curr['motion'] = True
        return curr

    def _check_status(self, curr):
        self._check_status_light(curr)
        self._check_status_motion(curr)

    def _check_status_light(self, curr):
        prev = self.status
        # Checking Light state
        if prev['light'] != curr['light']:
            if curr['light']:
                self.publish("light")
            else:
                self.publish("dark")
            self.log(f"light: {prev['light']} -> {curr['light']}")

    def _check_status_motion(self, curr):
        prev = self.status
        # Checking PIR state
        if prev['motion_raw'] != curr['motion_raw']:
            if curr['motion_raw']:
                self.motion_timeout_limit = 0
            else:
                self.motion_timeout_limit = curr['last_motion'] + (self.motion_timeout - 30 if self.motion_timeout > 30 else 0)
            self.log(f"motion_raw: {prev['motion_raw']} -> {curr['motion_raw']}, last_motion: {prev['last_motion']} -> {curr['last_motion']}")
        if prev['motion'] != curr['motion']:
            if curr['motion'] == True:
                self.publish("motion")
            else:
                if self.ignore_motion_timeout:
                    self.ignore_motion_timeout = False
                else:
                    self.publish("no_motion")
            self.log(f"motion: {prev['motion']} -> {curr['motion']}, last_motion: {prev['last_motion']} -> {curr['last_motion']}")

    def __str__(self):
        return f"{self.__class__.__name__}: battery={self.battery}, light={self.light}, motion_raw={curr['motion_raw']}, motion={self.motion}, last_motion={curr['last_motion']}"
