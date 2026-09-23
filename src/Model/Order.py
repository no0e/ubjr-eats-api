from typing import Dict, Optional

from pydantic import BaseModel


class Order(BaseModel):
    id_order: Optional[int] = None
    username_customer: str
    username_delivery_driver: Optional[str] = None
    address: str
    items: Dict[str, int]
