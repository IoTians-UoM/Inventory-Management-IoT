import threading
import queue
import time
import asyncio
import RPi.GPIO as GPIO
from hardware import RFIDController, GPIOController, StateMachine, OLEDController
from utils import Mode, Message, Action, Type, ProductPayload, Component, Status, InventoryPayload, InventoryItem
import websockets
import json


modes = {
        Mode.TAG_WRITE: [Mode.INVENTORY_IN],
        Mode.INVENTORY_IN: [Mode.INVENTORY_OUT],
        Mode.INVENTORY_OUT: [Mode.TAG_WRITE],
    }

stateMachine = StateMachine(modes, Mode.INVENTORY_IN)
message_queue = queue.Queue()
processing_queue = queue.Queue()  # For processing incoming messages
oled = OLEDController()
btn1 = GPIOController(24, 'in', 'high')
btn2 = GPIOController(22, 'in', 'high')
btn3 = GPIOController(27, 'in', 'high')
btn4 = GPIOController(17, 'in', 'high')
btn5 = GPIOController(4, 'in', 'high')

oled.display_text("Welcome to", line=1)
oled.display_text("Inventory System", line=2)
oled.display_text("By IoTians", line=3)
time.sleep(3)
oled.clear()

def rfid_worker():
    """Thread worker that listens for button presses and reads RFID data."""
    try:
        rfid = RFIDController()

        while True:
            mode = stateMachine.get_state()
            print(f"Current mode: {mode}")
            if mode == Mode.TAG_WRITE:
                oled.display_text("Tag Write", line=1)
                oled.display_text("Scan RFID tag", line=2)
                uid = rfid.detect_tag()
                if uid:
                    oled.display_text("writing...", line=3)
                    rfid.write_data(8, "Hello, RFID!")
                    time.sleep(1)
                    message = f"Tag Write: {uid}"
                    print(message)
                    message_queue.put(message)
            else:
                if mode == Mode.INVENTORY_IN:
                    oled.display_text("Inventory In", line=1)
                else:
                    oled.display_text("Inventory Out", line=1)
                oled.display_text("Scan RFID tag", line=2)
                uid = rfid.detect_tag()
                if uid:
                    oled.display_text("reading...", line=3)
                    data = rfid.read_data(8)
                    time.sleep(1)
                    oled.display_text(f"{data}", line=3)
                    desc = f"Inventory {mode}: {uid}, {data}"
                    print(desc)
                    message = Message(action=Action.PRODUCT_GET_BY_ID.value, type=Type.REQUEST.value, message_id=uid, payload={"product_id": '1'}, timestamp=str(time.time()))
                    message_queue.put(message)
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
                stateMachine.transition()
                oled.display_text(stateMachine.get_state().value, line=3)
                time.sleep(1)
                message = f"Mode switched to: {stateMachine.get_state()}"
                print(message)
                message_queue.put(message)
            time.sleep(0.5)
    except Exception as e:
        print(f"Error in mode switch worker: {e}")


async def ws_worker():
    """Async worker that handles WebSocket communication (sending and receiving) with reconnection logic."""
    uri = "ws://192.168.112.97:8000"

    while True:  # Keep trying to connect if the WebSocket is down
        try:
            async with websockets.connect(uri) as ws:
                print("Connected to WebSocket server")

                async def send_messages():
                    """Send messages from the queue to WebSocket."""
                    while True:
                        try:
                            message = await asyncio.to_thread(message_queue.get)  # Get message in async way
                            if message:
                                print(f"Sending WebSocket Message: {message}")
                                await ws.send(json.dumps(message))
                                message_queue.task_done()
                        except Exception as e:
                            print(f"Error sending message: {e}")

                async def receive_messages():
                    """Listen for incoming messages from WebSocket."""
                    while True:
                        try:
                            response = await ws.recv()  # Receive a message
                            print(f"Received WebSocket Message: {response}")
                            processing_queue.put(json.loads(response)) 
                            # Handle the received message as needed
                        except websockets.exceptions.ConnectionClosed:
                            print("WebSocket connection closed, attempting to reconnect...")
                            break
                        except Exception as e:
                            print(f"Error receiving message: {e}")

                # Run both send and receive tasks concurrently
                await asyncio.gather(send_messages(), receive_messages())

        except (websockets.exceptions.WebSocketException, OSError) as e:
            print(f"WebSocket connection failed: {e}, retrying in 5 seconds...")
            await asyncio.sleep(5)  # Retry connection after 5 seconds

def run_ws_worker():
    """Runs the async WebSocket worker inside an asyncio event loop."""
    asyncio.run(ws_worker())


def process_messages():
    """Worker function to process messages from the processing queue."""
    while True:
        try:
            message = processing_queue.get()    
            if message:
                print(f"Processing Message: {message}")
                oled.clear()

                # Perform actions based on message type
                if message.get("action") == Action.PRODUCT_GET_BY_ID.value:
                    oled.display_text(message.get('payload').get('products')[0].get('name'), line=1)

                    qty = 1
                    confirm = False
                    while True:
                        oled.display_text(f"Qty: {qty}" , line=3)
                        if btn2.read():
                            qty -= 1 if qty > 1 else 1
                        elif btn3.read():
                            qty += 1
                        elif btn5.read():
                            confirm = True
                            break;
                        elif btn4.read() or btn1.read():
                            break;
                        time.sleep(0.2)
                        print(f'qty {qty}')
                
                    oled.clear()
                    if confirm:
                        oled.display_text('confirmed', line=2)
                        mode = stateMachine.get_state()
                        action = Action.INVENTORY_IN if mode == Mode.INVENTORY_IN else Action.INVENTORY_OUT
                        inventory_item = InventoryItem(product_id=message.get('payload').get('products')[0].get('id'),quantity=qty, timestamp=time.time())
                        payload = InventoryPayload(inventory_items=[inventory_item])
                        msg = Message(action=action, type=Type.RESPONSE, component=Component.IOT, message_id=time.time(), status=Status.SUCCESS, timestamp=time.time(), payload=payload)
                        message_queue.put(msg)
                    else:
                        oled.display_text('cancelled', line=2)


            processing_queue.task_done()
        except json.JSONDecodeError:
            print("Error: Received invalid JSON format")
        except Exception as e:
            print(f"Error processing message: {e}")


# Start the RFID worker thread (normal threading)
rfid_thread = threading.Thread(target=rfid_worker, daemon=True)
rfid_thread.start()

# Start the WebSocket worker inside its own async event loop
ws_thread = threading.Thread(target=run_ws_worker, daemon=True)
ws_thread.start()

# Start the mode switch worker thread (normal threading)
mode_thread = threading.Thread(target=mode_switch_worker, daemon=True)
mode_thread.start()

# Start the message processing worker thread
processing_thread = threading.Thread(target=process_messages, daemon=True)
processing_thread.start()


# Main thread loop
try:
    while True:
        time.sleep(1)  # Keep main thread running
except KeyboardInterrupt:
    print("Program interrupted.")
finally:
    GPIO.cleanup()
    print("Cleaned up resources and exiting.")
