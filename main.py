from hardware import RFIDController, GPIOController
import time

def main():

    rfid = RFIDController()
    buzz = GPIOController(5, "out")
    print("Starting RFID test...")
    
    if rfid.detect_tag():
        buzz.write(1)
        print("RFID tag detected. Proceeding with operations...")
        print("Writing data to sector 8: Hello RFID")
        if rfid.write_data(8, "Hello RFID"):
            print("Write successful!")
        print("Reading data from sector 8...")
        data = rfid.read_data(8)
        if data:
            print("Read successful:", data)
            print("Data read from RFID:", data)
        buzz.write(0)
    else:
        print("No RFID tag detected. Please place a tag near the reader.")
    
    print("Cleaning up resources...")
    rfid.cleanup()

if __name__ == '__main__':
    btn1 = GPIOController(24, "in", "high")
    buzz = GPIOController(5, "out")
    
    while True:
        main()
        time.sleep(0.5)
        if btn1.read():
            buzz.write(1)
            time.sleep(0.1)
            buzz.write(0)
            time.sleep(0.1)
            buzz.write(1)
            time.sleep(0.1)
            buzz.write(0)
            print("Button pressed. Exiting program.")
            break
