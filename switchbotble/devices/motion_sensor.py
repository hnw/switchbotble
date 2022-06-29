from bleak.backends.scanner import BLEDevice
from .base import SwitchBotDevice

# see: https://github.com/OpenWonderLabs/python-host/wiki/Motion-Sensor-BLE-open-API
# PIR = Passive infrared(IR) sensor, motion sensor

class MotionSensor(SwitchBotDevice):
    def __init__(self, d: BLEDevice, service_data: bytearray):
        self.motion_l_limit = 0
        self.motion_l_timeout = 180
        self.ignore_motion_timeout = False
        self.ignore_motion_l_timeout = False
        super().__init__(d, service_data)

    def clear_current_motion_timeout(self):
        if self.motion:
            self.ignore_motion_timeout = True
        if self.motion_l:
            self.ignore_motion_l_timeout = True

    def _update_properties(self, d: BLEDevice, service_data: bytearray):
        # Battery
        self.battery = service_data[2] & 0x7f
        # Light state
        self.light = True if service_data[5] & 0x02 else False
        # PIR state
        self.motion = True if service_data[1] & 0x40 else False
        self.last_motion = service_data[4] + service_data[3]*256 + ((service_data[5] & 0x80) >> 7)*65536
        self.motion_l = self.motion

    def _check_diff(self):
        self._check_diff_light()
        self._check_diff_motion()

    def _check_diff_light(self):
        # Checking Light state
        if self.prev['light'] != self.light:
            if self.light:
                self.publish("light")
            else:
                self.publish("dark")
            self.log(f"light: {self.prev['light']} -> {self.light}")

    def _check_diff_motion(self):
        # Checking PIR state
        if self.prev['motion'] != self.motion:
            if self.motion:
                self.publish("motion")
                self.motion_l_limit = 0
            else:
                if self.ignore_motion_timeout:
                    self.ignore_motion_timeout = False
                else:
                    self.publish("no_motion")
                    self.motion_l_limit = self.last_motion + self.motion_l_timeout - 30
            self.log(f"motion: {self.prev['motion']} -> {self.motion}, last_motion: {self.prev['last_motion']} -> {self.last_motion}")
        if not self.motion and self.last_motion < self.motion_l_limit:
            self.motion_l = True
        if self.prev['motion_l'] != self.motion_l:
            if self.motion_l == True:
                self.publish("motion_l")
            else:
                if self.ignore_motion_l_timeout:
                    self.ignore_motion_l_timeout = False
                else:
                    self.publish("no_motion_l")
            self.log(f"motion_l: {self.prev['motion_l']} -> {self.motion_l}, last_motion: {self.prev['last_motion']} -> {self.last_motion}")

    def __str__(self):
        return f"{self.__class__.__name__}: battery={self.battery}, light={self.light}, motion={self.motion}, motion_l={self.motion_l}, last_motion={self.last_motion}"
