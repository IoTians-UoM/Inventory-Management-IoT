from hardware import RFIDController, GPIOController
import time

def write_tag(data_to_write="Hello RFID", sector=8):
    # Create RFID and buzzer controllers
    rfid = RFIDController()
    buzz = GPIOController(5, "out")
    print("Starting RFID operation...")

    # Check if an RFID tag is detected
    if rfid.detect_tag():
        buzz.write(1)  # Provide immediate feedback (buzzer on)
        print("RFID tag detected. Proceeding with operations...")
        
        # Write data to the specified sector
        print(f"Writing data to sector {sector}: {data_to_write}")
        if rfid.write_data(sector, data_to_write):
            print("Write successful!")
        else:
            print("Write failed!")
        
        # Read data back from the tag for verification
        print(f"Reading data from sector {sector}...")
        data = rfid.read_data(sector)
        if data:
            print("Read successful:", data)
            print("Data read from RFID:", data)
        else:
            print("No data read from the tag.")
        buzz.write(0)
    else:
        print("No RFID tag detected. Please place a tag near the reader.")
    
    # Clean up the RFID resources
    rfid.cleanup()

if __name__ == '__main__':
    # Setup button for termination and buzzer for feedback
    btn1 = GPIOController(24, "in", "high")
    buzz = GPIOController(5, "out")
    
    try:
        # Main loop: continuously try to write a tag until a termination button is pressed
        while True:
            write_tag()  # Attempt to write to the tag
            time.sleep(0.5)  # Delay between attempts

            # Check if termination button is pressed
            if btn1.read():
                # Provide a quick buzzer pattern to indicate shutdown
                buzz.write(1)
                time.sleep(0.1)
                buzz.write(0)
                time.sleep(0.1)
                buzz.write(1)
                time.sleep(0.1)
                buzz.write(0)
                print("Button pressed. Exiting program.")
                break
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")
    finally:
        buzz.write(0)
