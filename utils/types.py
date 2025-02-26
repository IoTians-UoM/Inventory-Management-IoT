from enum import Enum
from typing import TypedDict, Union, List, Optional

class Status(str, Enum):
    SUCCESS = "success"
    ERROR = "error"

class Action(str, Enum):
    ADD_EDIT = "add_edit"
    DELETE = "delete"

class Type(str, Enum):
    TAG_WRITE_REQ = "tag_write_req"
    TAG_WRITE_RESP = "tag_write_resp"
    SYNC = "sync"
    PRODUCT = "product"
    INVENTORY = "inventory"
    PRODUCT_BY_ID = "product_by_id"
    INVENTORY_BY_ID = "inventory_by_id"
    INVENTORY_IN = "inventory_in"
    INVENTORY_OUT = "inventory_out"

class Mode(str, Enum):
    INVENTORY_IN = "inventory_in"
    INVENTORY_OUT = "inventory_out"
    TAG_WRITE = "tag_write"


# TypedDicts (Equivalent to TypeScript object types)
class Product(TypedDict):
    id: str
    name: str
    price: float
    quantity: int
    timestamp: str

class InventoryItem(TypedDict):
    product_id: str
    product_name: Optional[str]  # product_name is optional
    quantity: int
    timestamp: str

class ProductAction(TypedDict):
    product_id: Optional[str]  # product_id is optional
    action: Action
    product: Optional[Product]  # product is optional
    timestamp: str

class InventoryAction(TypedDict):
    inventory_id: Optional[str]  # inventory_id is optional
    action: Action
    inventory_item: Optional[InventoryItem]  # inventory_item is optional
    timestamp: str

class ModeSwitch(TypedDict):
    mode: Mode
    timestamp: str

# Union type for Message data field
MessageData = Union[
    Product, 
    InventoryItem, 
    ProductAction, 
    InventoryAction, 
    ModeSwitch, 
    List[Product], 
    List[InventoryItem], 
    str
]

class Message(TypedDict):
    type: Type
    message_id: str
    data: MessageData
    status: Status
    timestamp: str
