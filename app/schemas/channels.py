from typing import Optional
from pydantic import BaseModel


class ChannelCreate(BaseModel):
    name: str
    comment: str
    status: Optional[str] = "open"


class ChannelResponse(BaseModel):
    id: int
    name: str
    comment: str
    status: str
    request_count: int
    accepted_request_count: int

    class Config:
        from_attributes = True
