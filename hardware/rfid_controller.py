import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import time


class RFIDController:
    def __init__(self):
        # Initialize RFID reader (MFRC522)
        self.reader = MFRC522()

    def detect_tag(self):
        """
        Detect if an RFID tag is present.
        Returns the UID if detected, else None.
        """
        (status, TagType) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
        if status == self.reader.MI_OK:
            print(f"Tag detected, type: {TagType}")
            (status, uid) = self.reader.MFRC522_Anticoll()
            if status == self.reader.MI_OK:
                print(f"Tag UID: {uid}")
                return uid
        return None

    def write_data(self, sector: int, data: str):
        """
        Write data to a specific sector on the RFID tag.
        """
        uid = self.detect_tag()
        if not uid:
            print("No tag detected. Cannot write data.")
            return False

        # Authenticate sector
        if not self.authenticate(sector, uid):
            print(f"Authentication failed for sector {sector}.")
            return False

        # Prepare data (16 bytes required per block)
        data_to_write = data.ljust(16)[:16]
        data_list = [ord(c) for c in data_to_write]

        self.reader.MFRC522_Write(sector, data_list)
        print(f"Data successfully written to sector {sector}: {data_to_write}")
        return True

    def read_data(self, sector: int):
        """
        Read data from a specific sector on the RFID tag.
        """
        uid = self.detect_tag()
        if not uid:
            print("No tag detected. Cannot read data.")
            return None

        if not self.authenticate(sector, uid):
            print(f"Authentication failed for sector {sector}.")
            return None

        data = self.reader.MFRC522_Read(sector)
        if data:
            decoded_data = ''.join([chr(i) for i in data if i != 0])
            print(f"Data read from sector {sector}: {decoded_data}")
            return decoded_data
        else:
            print(f"Failed to read data from sector {sector}.")
            return None

    def authenticate(self, sector: int, uid: list):
        """
        Authenticate access to a sector using default key.
        """
        default_key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.reader.MFRC522_SelectTag(uid)
        status = self.reader.MFRC522_Auth(self.reader.PICC_AUTHENT1A, sector, default_key, uid)
        return status == self.reader.MI_OK

    def cleanup(self):
        """ Clean up GPIO and RFID reader resources. """
        GPIO.cleanup(25)
        print("Cleaned up GPIO and RFID reader.")
