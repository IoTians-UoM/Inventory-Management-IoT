from hardware import RFIDController  # Replace 'your_module' with the actual module name if saved separately

def main():
    # Define pin assignments based on the Raspberry Pi's BCM numbering
    SDA_PIN = 8      # Chip Select (SDA)
    SCK_PIN = 11     # SPI Clock (SCK)
    MOSI_PIN = 10    # Master Out Slave In (MOSI)
    MISO_PIN = 9     # Master In Slave Out (MISO)
    IRQ_PIN = 18     # Optional IRQ pin (use a free GPIO pin if needed)
    RST_PIN = 25     # Reset pin

    rfid = RFIDController(SDA_PIN, SCK_PIN, MOSI_PIN, MISO_PIN, IRQ_PIN, RST_PIN)
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
    main()
