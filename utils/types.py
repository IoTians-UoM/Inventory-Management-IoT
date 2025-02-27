from enum import Enum
from typing import TypedDict, List, Optional

class Status(Enum):
    SUCCESS = "success"
    ERROR = "error"

class Type(Enum):
    REQUEST = "request"
    RESPONSE = "response"

class Action(Enum):
    # Product Actions
    PRODUCT_ADD_EDIT = "product_add_edit"
    PRODUCT_DELETE = "product_delete"
    PRODUCT_GET_ALL = "product_get_all"
    PRODUCT_GET_BY_ID = "product_get_by_id"

    # Inventory Actions
    INVENTORY_ADD_EDIT = "inventory_add_edit"
    INVENTORY_DELETE = "inventory_delete"
    INVENTORY_GET_ALL = "inventory_get_all"
    INVENTORY_GET_BY_ID = "inventory_get_by_id"
    INVENTORY_IN = "inventory_in"
    INVENTORY_OUT = "inventory_out"

    # Tag Write Actions
    TAG_WRITE = "tag_write"

    # Sync Actions
    SYNC = "sync"

    # Mode Switch
    MODE_SWITCH = "mode_switch"

class Mode(Enum):
    INVENTORY_IN = "Inventory In"
    INVENTORY_OUT = "Inventory Out"
    TAG_WRITE = "Tag Write"

class Product(TypedDict):
    id: str
    name: str
    price: float
    quantity: int
    timestamp: str

class InventoryItem(TypedDict):
    id: str
    product_id: str
    product_name: Optional[str]
    quantity: int
    timestamp: str

class ProductPayload(TypedDict, total=False):
    product_id: Optional[str]
    products: Optional[List[Product]]
    timestamp: str

class InventoryPayload(TypedDict, total=False):
    inventory_id: Optional[str]
    inventory_items: Optional[List[InventoryItem]]
    timestamp: str

class ModeSwitch(TypedDict):
    mode: Mode
    timestamp: str

class SyncPayload(TypedDict):
    products: List[Product]
    inventory: List[InventoryItem]
    timestamp: str

class Component(Enum):
    WEB = "web"
    IOT = "iot"
    API = "api"

class Message(TypedDict, total=False):
    action: Action
    type: Type
    component: Component
    message_id: str
    payload: Optional[ProductPayload | InventoryPayload | ModeSwitch | SyncPayload | str]
    status: Optional[Status]
    timestamp: str