import threading
import queue
import time
import asyncio
import RPi.GPIO as GPIO
from hardware import RFIDController, GPIOController, StateMachine, OLEDController
from utils import Mode, Message, Action, Type, ProductPayload, Component, Status, InventoryPayload, InventoryItem, LocalDBUtility, Product, SyncPayload
import websockets
import json

# Modes & State Machine
modes = {
    Mode.TAG_WRITE: [Mode.INVENTORY_IN],
    Mode.INVENTORY_IN: [Mode.INVENTORY_OUT],
    Mode.INVENTORY_OUT: [Mode.TAG_WRITE],
}
stateMachine = StateMachine(modes, Mode.INVENTORY_IN)

# Queues for handling messages
message_queue = queue.Queue()
processing_queue = queue.Queue()
products_sync_queue = queue.Queue()
inventory_sync_queue = queue.Queue()
tag_to_write = ''


# Hardware Components
oled = OLEDController()
btn1 = GPIOController(24, 'in', 'high')
btn2 = GPIOController(22, 'in', 'high')
btn3 = GPIOController(27, 'in', 'high')
btn4 = GPIOController(17, 'in', 'high')
btn5 = GPIOController(4, 'in', 'high')
buzz = GPIOController(5, 'out', 'high')

# Local Database
schemas = {'product': Product, 'inventory': InventoryItem}
localDB = LocalDBUtility('db.json', schemas)

# Startup OLED Display
oled.display_text("Welcome to", line=1)
oled.display_text("Inventory System", line=2)
oled.display_text("By IoTians", line=3)
time.sleep(3)
oled.clear()


def rfid_worker():
    """Thread worker that listens for button presses and reads RFID data."""
    try:
        # from utils.local_db_utility import get_product_id_by_rfid  # Assuming this exists in local_db_utility

        rfid = RFIDController()
        while True:
            mode = stateMachine.get_state()
            oled.clear()
            oled.display_text(f"{mode.value}", line=1)

            if rfid.detect_tag():
                oled.display_text("Processing...", line=3)
                buzz.write(1)
                time.sleep(0.1)
                buzz.write(0)

                if mode == Mode.TAG_WRITE:
                    if tag_to_write == '':
                        oled.display_text("No data to write", line=3)
                        return
                    if rfid.write_data(5, tag_to_write):
                        print(f"Writing Tag: {tag_to_write}")
                        oled.display_text("Writing tag...", line=3)
                        time.sleep(0.5)
                        oled.display_text("Success!", line=3)
                        message_queue.put(f"Tag Write: {tag_to_write}")
                    else:
                        print(f"Failed to write tag: {tag_to_write}")
                        oled.display_text("Failed!", line=3)
                else:
                    id, data = rfid.read_data(5)
                    if data:
                        print(f"Reading Tag: {data}")
                        oled.display_text("Reading tag...", line=3)
                        time.sleep(0.5)
                        oled.display_text("Success!", line=3)
                        # message_queue.put(f"Tag Read: {data}")
                        message = Message(
                            action=Action.PRODUCT_GET_BY_ID.value,
                            type=Type.REQUEST.value,
                            message_id='1',
                            payload={
                                "product_id": '1',  # <-- Hardcoded line commented out
                                # "product_id": product_id  # <-- Fetched from DB
                            },
                            timestamp=str(time.time())
                        )
                        message_queue.put(message)  # Allow time to read
                    else:
                        print("Failed to read tag")
                        oled.display_text("Failed!", line=3)

                        # Lookup product ID from local DB using RFID UID
                        # product_id = get_product_id_by_rfid(uid)
            time.sleep(0.5)
    except Exception as e:
        print(f"Error in RFID worker: {e}")

def mode_switch_worker():
    """Thread worker that listens for mode switch button presses."""
    try:
        while True:
            if btn1.read():
                oled.clear()
                oled.display_text("Mode Switching...", line=1)
                time.sleep(0.5)
                
                stateMachine.transition()
                oled.clear()
                oled.display_text(f"Switched to:", line=1)
                oled.display_text(f"{stateMachine.get_state().value}", line=2)
                
                buzz.write(1)
                time.sleep(0.1)
                buzz.write(0)

                message_queue.put(f"Mode switched to: {stateMachine.get_state()}")
            time.sleep(0.5)
    except Exception as e:
        print(f"Error in mode switch worker: {e}")

async def ws_worker():
    """Async worker that handles WebSocket communication with reconnection logic."""
    uri = "ws://192.168.112.97:8000"
    retry_delay = 5

    while True:
        try:
            async with websockets.connect(uri) as ws:
                print("Connected to WebSocket server")
                
                async def send_messages():
                    while True:
                        try:
                            message = await asyncio.to_thread(message_queue.get)
                            if message:
                                await ws.send(json.dumps(message))
                                message_queue.task_done()
                        except Exception as e:
                            print(f"Error sending message: {e}")

                async def receive_messages():
                    while True:
                        try:
                            response = await ws.recv()
                            time.sleep(1)  # Allow reading time
                            processing_queue.put(json.loads(response))
                        except websockets.exceptions.ConnectionClosed:
                            print("WebSocket connection closed, reconnecting...")
                            break
                        except Exception as e:
                            print(f"Error receiving message: {e}")

                await asyncio.gather(send_messages(), receive_messages())
        except Exception as e:
            print(f"WebSocket connection failed: {e}, retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)  # Exponential backoff

def run_ws_worker():
    """Runs the async WebSocket worker inside an asyncio event loop."""
    asyncio.run(ws_worker())

def handle_tag_write_request(message):
    """Handles tag writing requests."""
    global tag_to_write
    tag_to_write = message.get('payload').get('product_id')

    oled.clear()
    oled.display_text("Tag Write Mode", line=1)
    oled.display_text("Place RFID Tag", line=2)

    buzz.write(1)
    time.sleep(0.2)
    buzz.write(0)

    stateMachine.transition(Mode.TAG_WRITE)

def process_messages():
    """Worker function to process messages from the processing queue."""
    while True:
        try:
            message = processing_queue.get()
            if message:
                action = message.get('action')
                if action == Action.PRODUCT_GET_BY_ID.value:
                    inventory_operations(message)
                elif action == Action.SYNC.value:
                    sync_manager(message)
                elif action == Action.TAG_WRITE.value:
                    handle_tag_write_request(message)
            processing_queue.task_done()
        except Exception as e:
            print(f"Error processing message: {e}")

def inventory_operations(message):
    """Handles inventory adjustments (adding/removing items)."""
    product = message.get('payload').get('products')[0]
    product_name = product.get('name')
    product_id = product.get('id')

    oled.clear()
    oled.display_text(product_name, line=1)
    oled.display_text('   -   +   o   x', line=3)  # Buttons legend

    qty = 1
    confirm = False
    while True:
        oled.display_text(f"Qty: {qty}", line=2)

        if btn2.read():  # Decrease quantity
            if qty > 1:
                qty -= 1
        elif btn3.read():  # Increase quantity
            qty += 1
        elif btn4.read():  # Confirm selection
            confirm = True
            break
        elif btn5.read() or btn1.read():  # Cancel selection
            break
        time.sleep(0.2)

    oled.clear()
    if confirm:
        oled.display_text('Confirmed!', line=2)
        buzz.write(1)
        time.sleep(0.3)
        buzz.write(0)

        # Determine inventory action based on mode
        mode = stateMachine.get_state()
        action = Action.INVENTORY_IN.value if mode == Mode.INVENTORY_IN else Action.INVENTORY_OUT.value

        # Create inventory update message
        inventory_item = InventoryItem(product_id=product_id, quantity=qty, timestamp=time.time())
        payload = InventoryPayload(inventory_items=[inventory_item])
        msg = Message(
            action=action,
            type=Type.RESPONSE.value,
            component=Component.IOT.value,
            message_id=str(time.time()),
            status=Status.SUCCESS.value,
            timestamp=str(time.time()),
            payload=payload
        )
        message_queue.put(msg)
    else:
        oled.display_text('Cancelled!', line=2)
        buzz.write(1)
        time.sleep(0.1)
        buzz.write(0)
    
    time.sleep(1)
    oled.clear()

def sync_manager(message):
    products_sync_queue.put(message.get('payload').get('products'))
    inventory_sync_queue.put(message.get('payload').get('inventory'))

def sync_worker():
    while True:
        try:
            time.sleep(1)

            products = localDB.read_all('product')
            inventory = localDB.read_all('inventory')

            payload = SyncPayload(products=products, inventory=inventory, timestamp=time.time())
            message = Message(action=Action.SYNC.value, type=Type.REQUEST.value, component=Component.IOT.value, timestamp=time.time(), payload=payload)
            message_queue.put(message)

            time.sleep(59)  # Sync interval
        except Exception as e:
            print(f"Error in syncing {e}")

# Start worker threads
threading.Thread(target=rfid_worker, daemon=True).start()
threading.Thread(target=run_ws_worker, daemon=True).start()
threading.Thread(target=mode_switch_worker, daemon=True).start()
threading.Thread(target=process_messages, daemon=True).start()
threading.Thread(target=sync_worker, daemon=True).start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("Cleaned up resources and exiting.")
