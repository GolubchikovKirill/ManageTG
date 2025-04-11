from fastapi import APIRouter
from pydantic import BaseModel

from services.pyrogram_service import TelegramAuth

router = APIRouter(prefix="/auth", tags=["Auth"])


class SendCodeRequest(BaseModel):
    phone_number: str


class SignInRequest(BaseModel):
    phone_number: str
    code: str
    phone_code_hash: str
    password: str | None = None


@router.post("/send-code")
async def send_code(data: SendCodeRequest):
    tg = TelegramAuth(data.phone_number)
    result = await tg.send_code()
    return result


@router.post("/verify-code")
async def verify_code(data: SignInRequest):
    tg = TelegramAuth(data.phone_number)
    result = await tg.sign_in(
        code=data.code,
        phone_code_hash=data.phone_code_hash,
        password=data.password
    )
    return result