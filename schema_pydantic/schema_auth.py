from typing import Optional
from pydantic import BaseModel


class SendCodeRequest(BaseModel):
    phone_number: str
    api_id: int
    api_hash: str
    proxy_id: int


class SignInRequest(BaseModel):
    phone_number: str
    api_id: int
    api_hash: str
    proxy_id: int
    code: str
    password: Optional[str] = None