from bleak.backends.scanner import BLEDevice
from .motion_sensor import MotionSensor

# see: https://github.com/OpenWonderLabs/python-host/wiki/Contact-Sensor-BLE-open-API
# PIR = Passive infrared(IR) sensor, motion sensor
# HAL = Hall effect sensor, contact sensor (open/close sensor)

class ContactSensor(MotionSensor):
    def __init__(self, d: BLEDevice, service_data: bytearray):
        self.virtual_pir_limit = 0
        super().__init__(d, service_data)

    def _map_fields(self, d: BLEDevice, service_data: bytearray):
        # Battery
        self.battery = service_data[2] & 0x7f
        # Light state
        self.light = True if service_data[3] & 0x01 else False
        # PIR state
        self.motion = True if service_data[1] & 0x40 else False
        self.last_motion = service_data[5] + service_data[4]*256 + ((service_data[3] & 0x80) >> 7)*65536
        self.motion_l = self.motion
        # HAL state
        self.contact = (service_data[3] & 0x06) >> 1 # 0:close / 1: open / 2: timeout not close
        self.last_contact = service_data[7] + service_data[6]*256 + ((service_data[3] & 0x40) >> 6)*65536
        self.closed = True if self.contact == 0 else False
        self.opened = not self.closed
        # Counters
        self.enter_count = (service_data[8] & 0xc0) >> 6
        self.exit_count = (service_data[8] & 0x30) >> 4
        self.button_count = service_data[8] & 0x0f

    def _check_diff(self):
        self._check_diff_light()
        self._check_diff_motion()
        self._check_diff_contact()
        self._check_diff_counter()

    def _check_diff_contact(self):
        # Checing HAL state
        published = False
        if self.prev['contact'] != self.contact or (self.prev['last_contact'] == 0 and self.last_contact > 60):
            # ハードウェア側のバグ対応: なぜかこの数値だけ遅れてリセットされるのでライブラリ側で先にリセットしておく
            self.last_contact = 0
        if self.prev['contact'] != self.contact:
            if self.closed:
                # 1 or 2 => 0
                self.publish("closed")
                published = True
            elif self.prev['closed']:
                # 0 => 1 or 2
                self.publish("opened")
                published = True
            elif self.contact == 1:
                # 2 => 1
                self.publish("closed")
                self.publish("opened")
                published = True
        elif self.closed and self.prev['last_contact'] > self.last_contact:
            # 0 => 0
            self.publish("opened")
            self.publish("closed")
            published = True
        elif self.opened and self.prev['last_contact'] > self.last_contact:
            # 1 => 1
            self.publish("closed")
            self.publish("opened")
            published = True
        if published:
            self.log(f"contact: {self.prev['contact']} -> {self.contact}, last_contact: {self.prev['last_contact']} -> {self.last_contact}")

    def _check_diff_counter(self):
        # Checing counter
        push_count = self.button_count - self.prev['button_count']
        if push_count < 0:
            push_count += 15
        self.push_count = push_count
        if self.prev['enter_count'] != self.enter_count and self.enter_count != 0:
            self.publish("entered")
            self.log(f"enter_count: {self.prev['enter_count']} -> {self.enter_count}")
        if self.prev['exit_count'] != self.exit_count and self.exit_count != 0:
            self.publish("exited")
            self.log(f"exit_count: {self.prev['exit_count']} -> {self.exit_count}")
        if push_count != 0 and self.button_count != 0:
            self.publish("pushed")
            self.log(f"button_count: {self.prev['button_count']} -> {self.button_count}")

    def __str__(self):
        return f"{self.__class__.__name__}: battery={self.battery}, light={self.light}, motion={self.motion}, motion_l={self.motion_l}, last_motion={self.last_motion}, hal={self.hal}, hal_utc={self.hal_utc}, enter_count={self.enter_count}, exit_count={self.exit_count}, button_count={self.button_count}"
