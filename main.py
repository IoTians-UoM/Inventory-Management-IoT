import threading
import queue
import time
import RPi.GPIO as GPIO
from hardware import RFIDController
from hardware import GPIOController
from utils import WebSocketClient  # Assuming you have this implemented

# Queue for WebSocket messages
message_queue = queue.Queue()
btn1 = GPIOController(4, 'in', 'high')

def rfid_read_worker():
    """Thread worker that listens for button presses and reads RFID data."""
    rfid = RFIDController()
    block = 5  # Change if necessary

    while True:
        # Wait for button press
        print("Waiting for button press...")
        if btn1.read():
            print("Button pressed.")
            uid = rfid.detect_tag()
            if uid:
                message = f"RFID Tag detected: {uid}"
                print(message)
                message_queue.put(message)
            else:
                print("No RFID tag detected.")

        time.sleep(0.5)  # Small debounce delay

async def ws_sender_worker():
    """Thread worker that sends messages from the queue to WebSocket."""
    # WebSocket client instance
    ws = WebSocketClient("ws://192.168.112.97:8000")
    await ws.connect()
    
    while True:
        try:
            message = message_queue.get()
            if message:
                print(f"Sending WebSocket Message: {message}")
                await ws.send_message(message)  # Send via WebSocket
                message_queue.task_done()
        except Exception as e:
            print(f"Error in WebSocket thread: {e}")

# Start the worker threads
rfid_thread = threading.Thread(target=rfid_read_worker, daemon=True)
ws_thread = threading.Thread(target=ws_sender_worker, daemon=True)

rfid_thread.start()
ws_thread.start()

try:
    while True:
        time.sleep(1)  # Keep main thread running
except KeyboardInterrupt:
    print("Program interrupted.")
finally:
    GPIO.cleanup()
    print("Cleaned up resources and exiting.")
