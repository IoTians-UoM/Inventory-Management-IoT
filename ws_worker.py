import asyncio
from utils import WebSocketClient

async def websocket_main(ws_url, queue):
    ws = WebSocketClient(ws_url)
    await ws.connect()
    try:
        while True:
            # Wait for a message from the queue.
            msg = await queue.get()
            # A None message signals shutdown.
            if msg is None:
                break
            topic, message = msg
            await ws.send_message(topic, message)
    finally:
        await ws.disconnect()

def start_websocket_thread(ws_url):
    # Create a new event loop for the async thread.
    loop = asyncio.new_event_loop()
    # Create a queue for sending messages to the websocket.
    queue = asyncio.Queue(loop=loop)

    # Define a target function to run the event loop.
    def run_loop():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(websocket_main(ws_url, queue))
    
    import threading
    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()
    return loop, queue, thread
