
from src.Model.User import User


class DeliveryDriver(User):
    username: str
    vehicle: str
    is_available: bool
