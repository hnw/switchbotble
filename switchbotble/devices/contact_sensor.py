from bleak.backends.scanner import BLEDevice, AdvertisementData
from .motion_sensor import MotionSensor

# see: https://github.com/OpenWonderLabs/python-host/wiki/Contact-Sensor-BLE-open-API
# PIR = Passive infrared(IR) sensor, motion sensor
# HAL = Hall effect sensor, contact sensor (open/close sensor)

class ContactSensor(MotionSensor):
    def __init__(self, d: BLEDevice, **kwargs):
        super().__init__(d, **kwargs)

    def _parse_advertisement_data(self, ad: AdvertisementData):
        service_data = bytearray(next(iter(ad.service_data.values())))
        curr = {
            'rssi': ad.rssi,
            # Battery
            'battery': service_data[2] & 0x7f,
            # Light state
            'light': bool(service_data[3] & 0x01),
            # PIR state
            'motion_raw': bool(service_data[1] & 0x40),
            'last_motion': service_data[5] + service_data[4]*256 + ((service_data[3] & 0x80) >> 7)*65536,
            'motion': bool(service_data[1] & 0x40),
            # HAL state
            'contact': (service_data[3] & 0x06) >> 1, # 0:close / 1: open / 2: timeout not close
            'last_contact': service_data[7] + service_data[6]*256 + ((service_data[3] & 0x40) >> 6)*65536,
            # Counters
            'enter_count': (service_data[8] & 0xc0) >> 6,
            'exit_count': (service_data[8] & 0x30) >> 4,
            'button_count': service_data[8] & 0x0f,
        }
        curr['closed'] = bool(curr['contact'] == 0)
        curr['opened'] = bool(curr['contact'] != 0)
        # ハードウェア側のバグ対応: last_contactの数字がcontactの変化より遅れてリセットされることがあるのでライブラリ側で先にリセットしておく
        prev = self.status
        if prev != None:
            if prev['contact'] != curr['contact'] or (prev['last_contact'] == 0 and curr['last_contact'] > 60):
                curr['last_contact'] = 0
        return curr

    def _check_status(self, curr):
        self._check_status_light(curr)
        self._check_status_motion(curr)
        self._check_status_contact(curr)
        self._check_status_counter(curr)

    def _check_status_contact(self, curr):
        prev = self.status
        # Checing HAL state
        published = False
        if prev['contact'] != curr['contact']:
            if curr['closed']:
                # 1 or 2 => 0
                self.publish("closed")
                published = True
            elif prev['closed']:
                # 0 => 1 or 2
                self.publish("opened")
                published = True
            elif curr['contact'] == 1:
                # 2 => 1
                self.publish("closed")
                self.publish("opened")
                published = True
        elif curr['closed'] and prev['last_contact'] > curr['last_contact']:
            # 0 => 0
            self.publish("opened")
            self.publish("closed")
            published = True
        elif curr['contact'] == 1 and prev['last_contact'] > curr['last_contact']:
            # 1 => 1
            self.publish("closed")
            self.publish("opened")
            published = True
        if published or (prev['contact'] != curr['contact']):
            self.log(f"contact: {prev['contact']} -> {curr['contact']}, last_contact: {prev['last_contact']} -> {curr['last_contact']}")

    def _check_status_counter(self, curr):
        prev = self.status
        # Checing counter
        push_count = curr['button_count'] - prev['button_count']
        if push_count < 0:
            push_count += 15
        self.push_count = push_count
        if prev['enter_count'] != curr['enter_count'] and curr['enter_count'] != 0:
            self.publish("entered")
            self.log(f"enter_count: {prev['enter_count']} -> {curr['enter_count']}")
        if prev['exit_count'] != curr['exit_count'] and curr['exit_count'] != 0:
            self.publish("exited")
            self.log(f"exit_count: {prev['exit_count']} -> {curr['exit_count']}")
        if push_count != 0 and curr['button_count'] != 0:
            self.publish("pushed")
            self.log(f"button_count: {prev['button_count']} -> {curr['button_count']}")

    def __str__(self):
        return f"{self.__class__.__name__}: battery={self.battery}, light={self.light}, motion_raw={self.motion_raw}, motion={self.motion}, last_motion={self.last_motion}, contact={self.contact}, hal_utc={self.last_contact}, enter_count={self.enter_count}, exit_count={self.exit_count}, button_count={self.button_count}"
