import time
from hardware import RFIDController  # Replace 'your_module' with the actual module name if saved separately

def main():
    # Define pin assignments based on the Raspberry Pi's BCM numbering
    SDA_PIN = 8      # Chip Select (SDA)
    SCK_PIN = 11     # SPI Clock (SCK)
    MOSI_PIN = 10    # Master Out Slave In (MOSI)
    MISO_PIN = 9     # Master In Slave Out (MISO)
    IRQ_PIN = 18     # Optional IRQ pin (use a free GPIO pin if needed)
    RST_PIN = 25     # Reset pin

    # Create an instance of the RFIDReaderWriter
    rfid = RFIDController(SDA_PIN, SCK_PIN, MOSI_PIN, MISO_PIN, IRQ_PIN, RST_PIN)
    
    try:
        print("Starting RFID test...")
        # Test writing data to the RFID module
        test_data = "Hello RFID"
        rfid.write(test_data, sector=8)
        
        # Pause briefly to allow any write operations to complete
        time.sleep(1)
        
        # Test reading data from the RFID module
        data = rfid.read(sector=8)
        print(f"Data read from RFID: {data}")
        
    except KeyboardInterrupt:
        print("Test interrupted by user.")
    finally:
        # Always clean up GPIO and SPI resources
        rfid.cleanup()
        print("Cleaned up resources.")

if __name__ == "__main__":
    main()
