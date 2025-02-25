from time import time

class Product:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price
        self.timestamp = time()

    def __str__(self):
        return f"{self.id} - {self.name} (${self.price})"
    

class InventoryItem:
    def __init__(self, product_id, quantity, action):
        self.product_id = product_id
        self.quantity = quantity
        self.action = action
        self.timestamp = time()

    def __str__(self):
        return f"{self.product} - {self.quantity} units ({self.action})"