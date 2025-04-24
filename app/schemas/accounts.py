from typing import Optional
from pydantic import BaseModel

class AccountBase(BaseModel):
    is_authorized: bool
    name: str
    last_name: str
    phone_number: str
    api_id: int
    api_hash: str
    proxy_id: Optional[int] = None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    is_authorized: Optional[bool] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    api_id: Optional[int] = None
    api_hash: Optional[str] = None
    proxy_id: Optional[int] = None


class AccountRead(AccountBase):
    id: int

    class Config:
        from_attributes = True