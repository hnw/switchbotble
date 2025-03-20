from bleak.backends.scanner import BLEDevice, AdvertisementData
from .motion_sensor import MotionSensor

# see: https://github.com/OpenWonderLabs/python-host/wiki/Contact-Sensor-BLE-open-API
# PIR (Passive infrared sensor) : motion sensor
# HAL (Hall effect sensor) : contact sensor (open/close sensor for door)

class ContactSensor(MotionSensor):

    def __init__(self, d: BLEDevice, **kwargs):
        super().__init__(d, **kwargs)

    def _parse_advertisement_data(self, ad: AdvertisementData):
        service_data = bytearray(next(iter(ad.service_data.values())))
        return {
            'rssi': ad.rssi,
            'battery': service_data[2] & 0x7f,
            # Light state
            'light': bool(service_data[3] & 0x01),
            # PIR state
            'motion_raw': bool(service_data[1] & 0x40),
            'last_motion': service_data[5] + service_data[4] * 256 + ((service_data[3] & 0x80) >> 7) * 65536,
            # HAL state
            'contact': (service_data[3] & 0x06) >> 1, # 0:close / 1: open / 2: timeout not close
            'last_contact': service_data[7] + service_data[6] * 256 + ((service_data[3] & 0x40) >> 6) * 65536,
            # Counters
            'enter_counter': (service_data[8] & 0xc0) >> 6,
            'exit_counter': (service_data[8] & 0x30) >> 4,
            'push_counter': service_data[8] & 0x0f,
        }

    def _process_status(self):
        super()._process_status()
        self.status['closed'] = bool(self.status['contact'] == 0)
        self.status['opened'] = bool(self.status['contact'] != 0)
        if self.prev_status != None:
            # ハードウェア側のバグ対応: last_contactの数字がcontactの変化より遅れてリセットされることがあるのでライブラリ側で先にリセットしておく
            if self.prev_status['contact'] != self.status['contact'] or (self.prev_status['last_contact'] == 0 and self.status['last_contact'] > 60):
                self.status['last_contact'] = 0
            # Checing counter
            push_count = self.status['push_counter'] - self.prev_status['push_counter']
            if push_count < 0:
                push_count += 15
            self.status['push_count'] = push_count

    def _publish_signal(self):
        self._publish_signal_about_light()
        self._publish_signal_about_motion()
        self._publish_signal_about_door()
        self._publish_signal_about_counter()

    def _publish_signal_about_door(self):
        # Checing HAL state
        published = False
        if self.prev_status['contact'] != self.status['contact']:
            if self.status['closed']:
                # 1 or 2 => 0
                self.publish("closed")
                published = True
            elif self.prev_status['closed']:
                # 0 => 1 or 2
                self.publish("opened")
                published = True
            elif self.status['contact'] == 1:
                # 2 => 1
                self.publish("closed")
                self.publish("opened")
                published = True
        elif self.status['closed'] and self.prev_status['last_contact'] > self.status['last_contact']:
            # 0 => 0
            self.publish("opened")
            self.publish("closed")
            published = True
        elif self.status['contact'] == 1 and self.prev_status['last_contact'] > self.status['last_contact']:
            # 1 => 1
            self.publish("closed")
            self.publish("opened")
            published = True
        if published or (self.prev_status['contact'] != self.status['contact']):
            self.log(f"contact: {self.prev_status['contact']} -> {self.status['contact']}, last_contact: {self.prev_status['last_contact']} -> {self.status['last_contact']}")

    def _publish_signal_about_counter(self):
        if self.prev_status['enter_counter'] != self.status['enter_counter'] and self.status['enter_counter'] != 0:
            self.publish("entered")
            self.log(f"enter_counter: {self.prev_status['enter_counter']} -> {self.status['enter_counter']}")
        if self.prev_status['exit_counter'] != self.status['exit_counter'] and self.status['exit_counter'] != 0:
            self.publish("exited")
            self.log(f"exit_counter: {self.prev_status['exit_counter']} -> {self.status['exit_counter']}")
        if self.status['push_count'] > 0 and self.status['push_counter'] != 0:
            self.publish("pushed")
            self.log(f"push_counter: {self.prev_status['push_counter']} -> {self.status['push_counter']}")
