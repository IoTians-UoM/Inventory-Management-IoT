from datetime import datetime

class InventoryManager:
    def __init__(self, websocket_client):
        """
        Handles business logic for inventory management using the provided WebSocket client.
        """
        self.client = websocket_client

    async def write_rfid(self, tag_id, item_name, quantity):
        timestamp = datetime.utcnow().isoformat() + "Z"
        return await self.client.send_message("write_rfid", {
            "tag_id": tag_id,
            "item_name": item_name,
            "quantity": quantity,
            "timestamp": timestamp
        })

    async def stock_in(self, tag_id, quantity):
        timestamp = datetime.utcnow().isoformat() + "Z"
        return await self.client.send_message("stock_in", {
            "tag_id": tag_id,
            "quantity": quantity,
            "timestamp": timestamp
        })

    async def stock_out(self, tag_id, quantity):
        timestamp = datetime.utcnow().isoformat() + "Z"
        return await self.client.send_message("stock_out", {
            "tag_id": tag_id,
            "quantity": quantity,
            "timestamp": timestamp
        })

    async def get_inventory_status(self, tag_id):
        return await self.client.send_message("inventory_status_request", {"tag_id": tag_id})