from typing import Optional

from pydantic import BaseModel


class Item(BaseModel):
    id_item: Optional[int] = None
    name_item: str
    price: int
    category: str
    stock: int
    exposed: bool = False
