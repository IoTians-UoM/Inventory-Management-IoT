import time
import asyncio
from hardware import RFIDController, GPIOController
from ws_worker import start_websocket_thread

def main():
    ws_url = "ws://192.168.112.97:8080"
    # Start the websocket async loop in a separate thread.
    loop, ws_queue, ws_thread = start_websocket_thread(ws_url)
    
    # Initialize hardware controllers.
    btn1 = GPIOController(24, "in", "high")
    buzz = GPIOController(5, "out")
    rfid = RFIDController()
    
    try:
        while True:
            print("Starting RFID test...")
            tag = rfid.detect_tag()
            if tag:
                # Provide a buzz feedback when a tag is detected.
                buzz.write(1)
                time.sleep(0.1)
                buzz.write(0)
                print("RFID tag detected. Proceeding with operations...")
                print("Writing data to sector 4: Hello RFID")
                if rfid.write_data(4, "Hello RFID"):
                    print("Write successful!")
                print("Reading data from sector 4...")
                data = rfid.read_data(4)
                if data:
                    print("Read successful:", data)
                    print("Data read from RFID:", data)
                    # Submit the message to the websocket thread.
                    asyncio.run_coroutine_threadsafe(ws_queue.put(("data", data)), loop)
                else:
                    print("No Data.")
                    asyncio.run_coroutine_threadsafe(ws_queue.put(("data", "No Data.")), loop)
                
                # Reset RFID state, if applicable.
                try:
                    rfid.reader.stop_crypto()
                except Exception as e:
                    print("Error calling stop_crypto:", e)
                
                print("Waiting for tag removal...")
                while rfid.detect_tag():
                    time.sleep(0.2)
            else:
                print("No RFID tag detected. Please place a tag near the reader.")
            
            time.sleep(0.5)
            
            # Check if the exit button is pressed.
            if btn1.read():
                # Provide a quick buzz feedback pattern.
                buzz.write(1)
                time.sleep(0.1)
                buzz.write(0)
                time.sleep(0.1)
                buzz.write(1)
                time.sleep(0.1)
                buzz.write(0)
                # Signal the websocket thread to shut down.
                asyncio.run_coroutine_threadsafe(ws_queue.put(None), loop)
                print("Button pressed. Exiting program.")
                break
    finally:
        # Cleanup hardware.
        rfid.cleanup()
        buzz.cleanup()
        btn1.cleanup()
        # Stop the websocket event loop.
        loop.call_soon_threadsafe(loop.stop)
        ws_thread.join()

if __name__ == '__main__':
    main()
