import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import time

class RFIDController:
    def __init__(self):
        self.reader = MFRC522()

    def detect_tag(self):
        (status, tag_type) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
        if status == self.reader.MI_OK:
            (status, uid) = self.reader.MFRC522_Anticoll()
            if status == self.reader.MI_OK:
                print("Tag detected, UID:", uid)
                return uid
        return None

    def authenticate(self, block, uid):
        default_key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.reader.MFRC522_SelectTag(uid)
        status = self.reader.MFRC522_Auth(self.reader.PICC_AUTHENT1A, block, default_key, uid)
        if status == self.reader.MI_OK:
            return True
        else:
            print("Authentication failed for block", block)
            return False

    def write_data(self, block, data):
        uid = self.detect_tag()
        if uid is None:
            print("No tag detected. Cannot write data.")
            return False

        time.sleep(0.2)

        if not self.authenticate(block, uid):
            return False

        data_str = data.ljust(16)[:16]
        data_list = [ord(c) for c in data_str]
        print(f"Writing to block {block}: '{data_str}'")
        # status = self.reader.MFRC522_Write(block, data_list)
        try:
            status = self.reader.MFRC522_Write(block, data_list)
        except Exception as e:
            print(f"Error while writing to block {block}: {e}")
            return False

        print("MFRC522_Write returned:", status)
        if status == self.reader.MI_OK:
            print("Data successfully written.")
            return True
        else:
            print("Write operation failed with status", status)
            return False

    def read_data(self, block):
        uid = self.detect_tag()
        if uid is None:
            print("No tag detected. Cannot read data.")
            return None

        time.sleep(0.2)

        if not self.authenticate(block, uid):
            return None

        data = self.reader.MFRC522_Read(block)
        if data:
            decoded = ''.join(chr(i) for i in data if i != 0)
            print(f"Data read from block {block}: '{decoded}'")
            return decoded
        else:
            print("Failed to read data from block", block)
            return None

    def cleanup(self):
        # Corrected cleanup: remove the invalid channel parameter.
        GPIO.cleanup()
        print("Cleaned up GPIO and RFID resources.")