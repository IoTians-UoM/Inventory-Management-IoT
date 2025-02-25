from pirc522 import RFID
import RPi.GPIO as GPIO
import time


class RFIDController:
    def __init__(self):
        # Initialize RFID reader
        self.rdr = RFID()
        self.util = self.rdr.util()
        self.util.debug = False  # Set to True for debugging

    def detect_tag(self):
        """
        Detect if an RFID tag is present.
        Returns the UID if detected, else None.
        """
        self.rdr.wait_for_tag()
        (error, tag_type) = self.rdr.request()
        if not error:
            print(f"Tag detected, type: {tag_type}")
            (error, uid) = self.rdr.anticoll()
            if not error:
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

        # Select the tag
        self.rdr.select_tag(uid)

        # Authenticate sector
        if not self.authenticate(sector, uid):
            print(f"Authentication failed for sector {sector}.")
            return False

        # Prepare data (16 bytes required per block)
        data_to_write = data.ljust(16)[:16].encode('utf-8')

        (error, _) = self.rdr.write(sector, list(data_to_write))
        if not error:
            print(f"Data successfully written to sector {sector}.")
            return True
        else:
            print(f"Failed to write data to sector {sector}.")
            return False

    def read_data(self, sector: int):
        """
        Read data from a specific sector on the RFID tag.
        """
        uid = self.detect_tag()
        if not uid:
            print("No tag detected. Cannot read data.")
            return None

        self.rdr.select_tag(uid)

        if not self.authenticate(sector, uid):
            print(f"Authentication failed for sector {sector}.")
            return None

        (error, data) = self.rdr.read(sector)
        if not error:
            print(f"Data read from sector {sector}: {data}")
            return bytes(data).decode('utf-8', errors='ignore').strip()
        else:
            print(f"Failed to read data from sector {sector}.")
            return None

    def authenticate(self, sector: int, uid: list):
        """
        Authenticate access to a sector.
        Default key: [0xFF] * 6 for many RFID tags.
        """
        default_key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        (error, _) = self.rdr.auth(self.rdr.auth_a, sector, default_key, uid)
        return not error

    def cleanup(self):
        """ Clean up GPIO and RFID reader resources. """
        self.rdr.cleanup()
        GPIO.cleanup()
        print("Cleaned up GPIO and RFID reader.")


# ✅ Example usage
if __name__ == "__main__":
    controller = RFIDController()

    try:
        print("RFID Controller started. Press Ctrl+C to stop.")
        while True:
            tag_uid = controller.detect_tag()
            if tag_uid:
                print(f"Tag UID detected: {tag_uid}")
                if controller.write_data(8, "InventoryData"):
                    print("Write successful.")
                data_read = controller.read_data(8)
                if data_read:
                    print(f"Read data: {data_read}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping RFID Controller.")
    finally:
        controller.cleanup()
