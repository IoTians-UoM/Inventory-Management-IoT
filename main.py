from hardware import RFIDController, GPIOController

def main():

    rfid = RFIDController()
    print("Starting RFID test...")
    
    if rfid.detect_tag():
        print("RFID tag detected. Proceeding with operations...")
        print("Writing data to sector 8: Hello RFID")
        if rfid.write_data(8, "Hello RFID"):
            print("Write successful!")
        print("Reading data from sector 8...")
        data = rfid.read_data(8)
        if data:
            print("Read successful:", data)
            print("Data read from RFID:", data)
    else:
        print("No RFID tag detected. Please place a tag near the reader.")
    
    print("Cleaning up resources...")
    rfid.cleanup()

if __name__ == '__main__':
    btn1 = GPIOController(24, "in", "down")
    while True:
        main()
        if btn1.read():
            print("Button 1 pressed")
            break
