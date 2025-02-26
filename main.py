import threading
import queue
import time
import RPi.GPIO as GPIO
from hardware import RFIDController
from utils import WebSocketClient  # Assuming you have this implemented

# Define GPIO pin for button
BUTTON_PIN = 4

# Setup GPIO for button
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Queue for WebSocket messages
message_queue = queue.Queue()

# WebSocket client instance
ws = WebSocketClient("ws://192.168.112.97:8000")
ws.connect()

def rfid_read_worker():
    """Thread worker that listens for button presses and reads RFID data."""
    rfid = RFIDController()
    block = 5  # Change if necessary

    while True:
        # Wait for button press
        GPIO.wait_for_edge(BUTTON_PIN, GPIO.FALLING)
        print("Button pressed. Reading RFID tag...")

        data = rfid.read_data(block)
        if data:
            print(f"RFID Data Read: {data}")
            message_queue.put(data)  # Queue the message for WebSocket sending
        else:
            print("Failed to read data from RFID tag.")

        time.sleep(0.5)  # Small debounce delay

def ws_sender_worker():
    """Thread worker that sends messages from the queue to WebSocket."""
    while True:
        try:
            message = message_queue.get()
            if message:
                print(f"Sending WebSocket Message: {message}")
                ws.send_message(message)  # Send via WebSocket
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
    ws.disconnect()
    print("Cleaned up resources and exiting.")
