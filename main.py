from hardware import RFIDController
import time
import RPi.GPIO as GPIO

def main():
    rfid = RFIDController()
    block = 5  # Change this if necessary; verify if block 5 is writable.
    data_to_write = "Hello RFID"
    print("Please keep the tag near the reader.")
    time.sleep(2)

    if rfid.write_data(block, data_to_write):
        time.sleep(0.5)
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
        GPIO.cleanup()  # Remove duplicate cleanup if already done.
