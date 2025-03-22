from bleak.backends.scanner import BLEDevice, AdvertisementData
from .base import SwitchBotDevice

# see: https://github.com/OpenWonderLabs/python-host/wiki/Motion-Sensor-BLE-open-API
# PIR = Passive infrared(IR) sensor, motion sensor

class MotionSensor(SwitchBotDevice):
    def __init__(self, d: BLEDevice, motion_timeout: int = 30, **kwargs):
        self.motion_timeout_limit = 0
        self.motion_timeout = motion_timeout
        self.ignore_motion_timeout = False
        super().__init__(d, **kwargs)

    def clear_current_motion_timeout(self):
        if self.status['motion'] == True:
            self.ignore_motion_timeout = True

    def _parse_advertisement_data(self, ad: AdvertisementData):
        service_data = bytearray(next(iter(ad.service_data.values())))
        return {
            'rssi': ad.rssi,
            # Battery value
            'battery': service_data[2] & 0x7f,
            # Light state
            'light': bool(service_data[5] & 0x02),
            # PIR state
            'motion_raw': bool(service_data[1] & 0x40),
            'last_motion': service_data[4] + service_data[3] * 256 + ((service_data[5] & 0x80) >> 7) * 65536,
        }

    def _process_status(self):
        self.status['motion'] = self.status['motion_raw']
        if self.prev_status != None and self.prev_status['motion_raw'] != self.status['motion_raw']:
            if self.status['motion_raw'] == True:
                self.motion_timeout_limit = 0
            else:
                timeout_delta = self.motion_timeout - 30
                if timeout_delta < 0:
                    timeout_delta = 0
                self.motion_timeout_limit = self.status['last_motion'] + timeout_delta
        if self.status['motion_raw'] == False and self.status['last_motion'] < self.motion_timeout_limit:
            self.status['motion'] = True

    def _publish_signal(self):
        self._publish_signal_about_light()
        self._publish_signal_about_motion()

    def _publish_signal_about_light(self):
        # Checking Light state
        if self.prev_status['light'] != self.status['light']:
            if self.status['light']:
                self.publish("light")
            else:
                self.publish("dark")
            self.log(f"light: {self.prev_status['light']} -> {self.status['light']}")

    def _publish_signal_about_motion(self):
        # Checking PIR state
        if self.prev_status['motion_raw'] != self.status['motion_raw']:
            self.log(f"motion_raw: {self.prev_status['motion_raw']} -> {self.status['motion_raw']}, last_motion: {self.prev_status['last_motion']} -> {self.status['last_motion']}")
        if self.prev_status['motion'] != self.status['motion']:
            if self.status['motion'] == True:
                self.publish("motion")
            else:
                if self.ignore_motion_timeout:
                    self.ignore_motion_timeout = False
                else:
                    self.publish("no_motion")
            self.log(f"motion: {self.prev_status['motion']} -> {self.status['motion']}, last_motion: {self.prev_status['last_motion']} -> {self.status['last_motion']}")
