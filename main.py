import threading
import queue
import time
import asyncio
import RPi.GPIO as GPIO
from hardware import RFIDController, GPIOController, StateMachine, OLEDController
from utils import WebSocketClient, Mode


modes = {
        Mode.TAG_WRITE: [Mode.INVENTORY_IN],
        Mode.INVENTORY_IN: [Mode.INVENTORY_OUT],
        Mode.INVENTORY_OUT: [Mode.TAG_WRITE],
    }

stateMachine = StateMachine(modes, Mode.INVENTORY_IN)
message_queue = queue.Queue()
oled = OLEDController()
btn5 = GPIOController(4, 'in', 'high')
btn1 = GPIOController(24, 'in', 'high')

oled.display_text("Welcome to", line=1)
oled.display_text("Inventory System", line=2)
oled.display_text("By IoTians", line=3)
time.sleep(3)

def rfid_worker():
    """Thread worker that listens for button presses and reads RFID data."""
    try:
        rfid = RFIDController()

        while True:
            uid = rfid.detect_tag()
            mode = stateMachine.get_state()
            if uid:
                oled.clear()
                if mode == Mode.TAG_WRITE:
                    oled.display_text("Tag Write", line=1)
                    oled.display_text("Scan RFID tag", line=2)
                    rfid.write_data(5, "Hello, RFID!")
                    message = f"Tag Write: {uid}"
                    print(message)
                    message_queue.put(message)
                else:
                    oled.display_text("Inventory In", line=1)
                    oled.display_text("Scan RFID tag", line=2)
                    if mode == Mode.INVENTORY_IN:
                        message = f"Inventory In: {uid}"
                    else:
                        message = f"Inventory Out: {uid}"
                    print(message)
                    message_queue.put(message)
            else:
                print("No RFID tag detected.")
            time.sleep(0.5)
    except Exception as e:
        print(f"Error in RFID worker: {e}")


def mode_switch_worker():
    """Thread worker that listens for mode switch button presses."""
    try:
        while True:
            if btn1.read():
                oled.clear()
                oled.display_text("Mode Switch", line=1)
                oled.display_text("to", line=2)
                oled.display_text(stateMachine.get_state().value, line=3)
                stateMachine.transition()
                message = f"Mode switched to: {stateMachine.get_state()}"
                print(message)
                message_queue.put(message)
            time.sleep(0.5)
    except Exception as e:
        print(f"Error in mode switch worker: {e}")


async def ws_sender_worker():
    """Async worker that sends messages from the queue to WebSocket."""
    ws = WebSocketClient("ws://192.168.112.97:8000")
    await ws.connect()
    
    while True:
        try:
            message = await asyncio.to_thread(message_queue.get)  # Get message in async way
            if message:
                print(f"Sending WebSocket Message: {message}")
                await ws.send_message('detect', message)  # Send via WebSocket
                message_queue.task_done()
        except Exception as e:
            print(f"Error in WebSocket thread: {e}")

def run_ws_worker():
    """Runs the async WebSocket worker inside an asyncio event loop."""
    asyncio.run(ws_sender_worker())


# Start the RFID worker thread (normal threading)
rfid_thread = threading.Thread(target=rfid_worker, daemon=True)
rfid_thread.start()

# # Start the WebSocket worker inside its own async event loop
# ws_thread = threading.Thread(target=run_ws_worker, daemon=True)
# ws_thread.start()

# Start the mode switch worker thread (normal threading)
mode_thread = threading.Thread(target=mode_switch_worker, daemon=True)
mode_thread.start()


# Main thread loop
try:
    while True:
        time.sleep(1)  # Keep main thread running
except KeyboardInterrupt:
    print("Program interrupted.")
finally:
    GPIO.cleanup()
    print("Cleaned up resources and exiting.")
