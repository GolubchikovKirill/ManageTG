from pydantic import BaseModel


class AddProxyRequest(BaseModel):
    ip_address: str
    login: str
    password: str
    port: int