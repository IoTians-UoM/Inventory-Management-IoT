import RPi.GPIO as GPIO
import time

class LCD1602:
    def __init__(self, rs, e, d4, d5, d6, d7):
        self.rs = rs
        self.e = e
        self.data_pins = [d4, d5, d6, d7]

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.rs, GPIO.OUT)
        GPIO.setup(self.e, GPIO.OUT)
        for pin in self.data_pins:
            GPIO.setup(pin, GPIO.OUT)

        self.initialize_display()

    def pulse_enable(self):
        GPIO.output(self.e, False)
        time.sleep(0.0005)
        GPIO.output(self.e, True)
        time.sleep(0.0005)
        GPIO.output(self.e, False)
        time.sleep(0.0005)

    def send_nibble(self, data):
        for i in range(4):
            GPIO.output(self.data_pins[i], bool(data & (1 << i)))
        self.pulse_enable()

    def send_byte(self, data, mode):
        GPIO.output(self.rs, mode)
        self.send_nibble(data >> 4)
        self.send_nibble(data & 0x0F)
        time.sleep(0.0005)

    def initialize_display(self):
        self.send_byte(0x33, False)
        self.send_byte(0x32, False)
        self.send_byte(0x28, False)
        self.send_byte(0x0C, False)
        self.send_byte(0x06, False)
        self.clear()

    def clear(self):
        self.send_byte(0x01, False)
        time.sleep(0.002)

    def write_message(self, message, line=1):
        line_addresses = {1: 0x80, 2: 0xC0}
        if line in line_addresses:
            self.send_byte(line_addresses[line], False)
            for char in message.ljust(16):
                self.send_byte(ord(char), True)

    def cleanup(self):
        GPIO.cleanup()


