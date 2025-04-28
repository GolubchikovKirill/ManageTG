from typing import Optional
from pydantic import BaseModel, model_validator


class SendCodeRequest(BaseModel):
    phone_number: str
    api_id: int
    api_hash: str
    proxy_id: int

    @model_validator(mode="before")
    def add_plus_if_missing(cls, values):
        phone = values.get('phone_number')

        if not phone:
            raise ValueError("Phone number is required")

        phone = phone.strip()

        if not phone.startswith('+'):
            phone = '+' + phone

        if not phone[1:].isdigit():
            raise ValueError("Phone number must contain only digits after '+'")

        values['phone_number'] = phone
        return values


class SignInRequest(BaseModel):
    phone_number: str
    code: str
    password: Optional[str] = None
    api_id: int
    api_hash: str
    proxy_id: int

    @model_validator(mode="before")
    def add_plus_if_missing(cls, values):
        phone = values.get('phone_number')

        if not phone:
            raise ValueError("Phone number is required")

        phone = phone.strip()

        if not phone.startswith('+'):
            phone = '+' + phone

        if not phone[1:].isdigit():
            raise ValueError("Phone number must contain only digits after '+'")

        values['phone_number'] = phone
        return values
