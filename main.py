import asyncio
from hardware import RFIDController, GPIOController
from utils import WebSocketClient
import time

async def main_loop(ws, btn1, buzz, rfid):
    try:
        while True:
            print("Starting RFID test...")
            tag = rfid.detect_tag()
            if tag:
                # Provide a quick buzz feedback when a tag is detected
                buzz.write(1)
                await asyncio.sleep(0.1)
                buzz.write(0)
                print("RFID tag detected. Proceeding with operations...")
                print("Writing data to sector 8: Hello RFID")
                if rfid.write_data(4, "Hello RFID"):
                    print("Write successful!")
                print("Reading data from sector 8...")
                data = rfid.read_data(4)
                if data:
                    print("Read successful:", data)
                    print("Data read from RFID:", data)
                    await ws.send_message('data', data)
                else:
                    print("No Data.")
                    await ws.send_message('data', "No Data.")
                
                # Wait until the tag is removed before continuing.
                print("Waiting for tag removal...")
                while rfid.detect_tag():
                    await asyncio.sleep(0.2)
            else:
                print("No RFID tag detected. Please place a tag near the reader.")
            
            # Wait a short time before next cycle.
            await asyncio.sleep(0.5)
            
            # Check if the exit button is pressed.
            if btn1.read():
                # Provide a quick buzz feedback pattern.
                buzz.write(1)
                await asyncio.sleep(0.1)
                buzz.write(0)
                await asyncio.sleep(0.1)
                buzz.write(1)
                await asyncio.sleep(0.1)
                buzz.write(0)
                await ws.disconnect()
                print("Button pressed. Exiting program.")
                break
    finally:
        # Cleanup all resources once before exit.
        rfid.cleanup()
        buzz.cleanup()
        btn1.cleanup()

async def async_main():
    # Initialize controllers once.
    btn1 = GPIOController(24, "in", "high")
    buzz = GPIOController(5, "out")
    rfid = RFIDController()
    ws = WebSocketClient("ws://192.168.112.97:8080")
    
    # Connect the async WebSocket.
    await ws.connect()
    await ws.send_message("status", "IoT connected.")
    await main_loop(ws, btn1, buzz, rfid)

if __name__ == '__main__':
    asyncio.run(async_main())
