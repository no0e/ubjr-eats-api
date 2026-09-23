from abc import ABC

from pydantic import BaseModel


class User(BaseModel, ABC):
    username: str
    firstname: str
    lastname: str
    password: str
    salt: str
    account_type: str
