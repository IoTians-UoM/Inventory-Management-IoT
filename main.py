import threading
import queue
import time
import asyncio
import RPi.GPIO as GPIO
from hardware import RFIDController, GPIOController, StateMachine, OLEDController
from utils import Mode, Message, Action, Type, ProductPayload, Component, Status, InventoryPayload, InventoryItem, LocalDBUtility, Product, SyncPayload
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
products_sync_queue = queue.Queue()
inventory_sync_queue = queue.Queue()
tag_to_write = ''
oled = OLEDController()
btn1 = GPIOController(24, 'in', 'high')
btn2 = GPIOController(22, 'in', 'high')
btn3 = GPIOController(27, 'in', 'high')
btn4 = GPIOController(17, 'in', 'high')
btn5 = GPIOController(4, 'in', 'high')
buzz = GPIOController(5, 'out', 'high')

schemas = {'product':Product,'inventory':InventoryItem}
localDB = LocalDBUtility('db.json', schemas)


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
                    time.sleep(0.5)
                    if rfid.write_data(4, tag_to_write):
                        buzz.write(1)
                        time.sleep(0.5)
                        buzz.write(0)
                        oled.display_text("success", line=3)
                        message = f"Tag Write: {uid}"
                        print(message)
                        message_queue.put(message)
                    else:
                        oled.display_text("failed", line=3)
                time.sleep(0.5)
            else:
                if mode == Mode.INVENTORY_IN:
                    oled.display_text("Inventory In", line=1)
                else:
                    oled.display_text("Inventory Out", line=1)
                oled.display_text("Scan RFID tag", line=2)
                uid = rfid.detect_tag()
                if uid:
                    oled.display_text("reading...", line=3)
                    buzz.write(1)
                    data = rfid.read_data(4)
                    time.sleep(0.1)
                    buzz.write(0)
                    oled.display_text(f"{data}", line=3)
                    desc = f"Inventory {mode}: {uid}, {data}"
                    print(desc)
                    message = Message(action=Action.PRODUCT_GET_BY_ID.value, type=Type.REQUEST.value, message_id=uid, payload={"product_id": '1'}, timestamp=str(time.time()))
                    message_queue.put(message)
                time.sleep(0.5)
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
                buzz.write(1)
                time.sleep(0.1)
                buzz.write(0)
                time.sleep(0.1)
                buzz.write(1)
                time.sleep(0.1)
                buzz.write(0)
                time.sleep(0.2)
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


def handle_tag_write_request(message):
    tag_to_write = message.get('payload').get('product_id')
    stateMachine.transition(Mode.TAG_WRITE.value)
    buzz.write(1)
    time.sleep(0.2)
    buzz.write(0)


def process_messages():
    """Worker function to process messages from the processing queue."""
    while True:
        try:
            message = processing_queue.get()    
            if message:
                print(f"Processing Message: {message}")
                action = message.get('action')

                # Perform actions based on message type
                if action == Action.PRODUCT_GET_BY_ID.value:
                    inventory_operations(message)
                elif action == Action.SYNC.value:
                    sync_manager(message)
                elif action == Action.TAG_WRITE.value:
                    handle_tag_write_request(message)

            processing_queue.task_done()
        except json.JSONDecodeError:
            print("Error: Received invalid JSON format")
        except Exception as e:
            print(f"Error processing message: {e}")


def inventory_operations(message):
    oled.clear()
    oled.display_text(message.get('payload').get('products')[0].get('name'), line=1)
    oled.display_text('   -   +   o   x',line=3)

    qty = 1
    confirm = False
    while True:
        oled.display_text(f"Qty: {qty}" , line=2)
        if btn2.read():
            if qty > 1:
                qty -= 1
                print(f'qty {qty}')
        elif btn3.read():
            qty += 1
            print(f'qty {qty}')
        elif btn4.read():
            confirm = True
            break;
        elif btn5.read() or btn1.read():
            break;
        time.sleep(0.2)

    if confirm:
        oled.display_text('..confirmed', line=3)
        buzz.write(1)
        time.sleep(0.3)
        buzz.write(0)
        mode = stateMachine.get_state()
        action = Action.INVENTORY_IN.value if mode == Mode.INVENTORY_IN.value else Action.INVENTORY_OUT.value
        inventory_item = InventoryItem(product_id=message.get('payload').get('products')[0].get('id'),quantity=qty, timestamp=time.time())
        payload = InventoryPayload(inventory_items=[inventory_item])
        msg = Message(action=action, type=Type.RESPONSE.value, component=Component.IOT.value, message_id=time.time(), status=Status.SUCCESS.value, timestamp=time.time(), payload=payload)
        message_queue.put(msg)
    else:
        buzz.write(1)
        time.sleep(0.1)
        buzz.write(0)
        oled.display_text('..discarded', line=3)   


def sync_manager(message):
    products = message.get('payload').get('products')
    inventory = message.get('payload').get('inventory')

    products_sync_queue.put(products)
    inventory_sync_queue.put(inventory)



def sync_worker():
    while True:
        try:
            products = localDB.read_all('product')
            inventory = localDB.read_all('inventory')

            payload = SyncPayload(products=products, inventory=inventory, timestamp=time.time())
            message = Message(action=Action.SYNC.value, type=Type.REQUEST.value, component=Component.IOT.value, timestamp=time.time(), payload=payload)

            print("syncing...")
            message_queue.put(message)
            time.sleep(10)

            while True:
                p = products_sync_queue.get()
                if p:
                    localDB.upsert('product', p, 'id')
                    products_sync_queue.task_done()

                i = inventory_sync_queue.get()
                if i:
                    localDB.upsert('inventory', i, 'id')
                    inventory_sync_queue.task_done()

                print("ddddddddddddddddddddddddddddddd",p,i)
                if not p and not i:
                    break;
            
            # time.sleep(50)
        except Exception as e:
            print("Error in syncing")


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

# Start sync manager
sync_thread = threading.Thread(target=sync_worker, daemon=True)
sync_thread.start()


# Main thread loop
try:
    while True:
        time.sleep(1)  # Keep main thread running
except KeyboardInterrupt:
    print("Program interrupted.")
finally:
    GPIO.cleanup()
    print("Cleaned up resources and exiting.")
