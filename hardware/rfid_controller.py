import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import time

class RFIDController:
    def __init__(self):
        # Initialize the MFRC522 RFID reader
        self.reader = MFRC522()

    def detect_tag(self):
        """
        Check if an RFID tag is present.
        Returns the UID if detected, otherwise returns None.
        """
        (status, tag_type) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
        if status == self.reader.MI_OK:
            (status, uid) = self.reader.MFRC522_Anticoll()
            if status == self.reader.MI_OK:
                print("Tag detected, UID:", uid, "Type:", tag_type)
                return uid
        return None

    def authenticate(self, block, uid):
        """
        Authenticate the specified block (sector) on the tag using the default key.
        Returns True if authentication is successful.
        """
        default_key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.reader.MFRC522_SelectTag(uid)
        status = self.reader.MFRC522_Auth(self.reader.PICC_AUTHENT1A, block, default_key, uid)
        if status == self.reader.MI_OK:
            return True
        else:
            print("Authentication failed for block", block)
            return False

    def write_data(self, block, data):
        """
        Write a string (up to 16 characters) to the given block.
        Returns True on success, False on failure.
        """
        uid = self.detect_tag()
        if uid is None:
            print("Error: No tag detected. Cannot write data.")
            return False

        # Delay to ensure the tag remains in the field
        time.sleep(0.2)

        if not self.authenticate(block, uid):
            return False

        # Prepare data: pad or trim to 16 characters, then convert to list of integers
        data_str = data.ljust(16)[:16]
        data_list = [ord(c) for c in data_str]
        print(f"Writing to block {block}: '{data_str}'")

        status = self.reader.MFRC522_Write(block, data_list)
        if status == self.reader.MI_OK:
            print("Data successfully written.")
            return True
        else:
            print("Error: Write operation failed with status", status)
            return False

    def read_data(self, block):
        """
        Read data from the given block.
        Returns the data as a string if successful, or None if not.
        """
        uid = self.detect_tag()
        if uid is None:
            print("Error: No tag detected. Cannot read data.")
            return None

        # Delay to ensure stability before authentication
        time.sleep(0.2)

        if not self.authenticate(block, uid):
            return None

        data = self.reader.MFRC522_Read(block)
        if data:
            # Convert non-zero bytes to characters and combine into a string
            decoded = ''.join(chr(i) for i in data if i != 0)
            print(f"Data read from block {block}: '{decoded}'")
            return decoded
        else:
            print("Error: Read operation failed.")
            return None

    def cleanup(self):
        """Clean up GPIO resources."""
        GPIO.cleanup(25)
        print("Cleaned up GPIO and RFID resources.")