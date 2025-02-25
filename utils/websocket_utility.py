import asyncio
import websockets
import json

class InventoryWebSocketClient:
    def __init__(self, url):
        """
        Initialize the WebSocket client with the server URL.
        """
        self.url = url

    async def connect(self):
        """
        Establish a WebSocket connection.
        """
        self.connection = await websockets.connect(self.url)
        print("Connected to WebSocket server.")

    async def disconnect(self):
        """
        Close the WebSocket connection.
        """
        await self.connection.close()
        print("Disconnected from WebSocket server.")

    async def send_message(self, message_type, data):
        """
        Send a generic message to the WebSocket server.
        """
        message = json.dumps({"type": message_type, "data": data})
        await self.connection.send(message)
        print(f"Sent: {message}")

    async def receive_message(self):
        """
        Receive a message from the WebSocket server.
        """
        response = await self.connection.recv()
        print(f"Received: {response}")
        return json.loads(response)