from hardware import RFIDController
import time
import RPi.GPIO as GPIO

def main():
    rfid = RFIDController()
    block = 8         # Block (sector) to write/read (verify your tag's writable block)
    data_to_write = "Hello RFID"

    print("Please keep the tag near the reader.")
    time.sleep(2)  # Allow time for the tag to be placed

    # Attempt to write data to the tag
    if rfid.write_data(block, data_to_write):
        # Short delay before reading back
        time.sleep(0.5)
        # Attempt to read data from the tag
        data = rfid.read_data(block)
        if data:
            print("Final read data:", data)
        else:
            print("Failed to read data from the tag.")
    else:
        print("Write operation failed.")

    rfid.cleanup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        GPIO.cleanup()