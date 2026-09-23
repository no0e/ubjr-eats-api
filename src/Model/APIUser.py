from pydantic import BaseModel


class APIUser(BaseModel):
    username: str
    account_type: str
