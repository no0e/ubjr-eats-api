from typing import List, Optional

from pydantic import BaseModel


class Delivery(BaseModel):
    id_delivery: Optional[int] = None
    username_delivery_driver: Optional[str] = None
    duration: Optional[int] = None
    id_orders: List[int] = []
    stops: List[str] = []
    is_accepted: bool
