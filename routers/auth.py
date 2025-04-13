from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.pyrogram_service import TelegramAuth
from services.session_control import SessionManager
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Auth"])

# Инициализация SessionManager
session_manager = SessionManager()

class SendCodeRequest(BaseModel):
    phone_number: str
    api_id: int
    api_hash: str

class SignInRequest(BaseModel):
    phone_number: str
    code: str
    phone_code_hash: str
    password: Optional[str] = None  # Используем Optional для параметра пароля
    api_id: int
    api_hash: str

@router.post("/send-code")
async def send_code(data: SendCodeRequest):
    try:
        tg = TelegramAuth(
            phone_number=data.phone_number,
            api_id=data.api_id,
            api_hash=data.api_hash,
            session_manager=session_manager
        )
        result = await tg.send_code()

        if result["status"] == "ok":
            return {"status": "ok", "phone_code_hash": result["phone_code_hash"]}
        else:
            raise HTTPException(status_code=500, detail="Failed to send code")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending code: {str(e)}")

@router.post("/verify-code")
async def verify_code(data: SignInRequest):
    try:
        tg = TelegramAuth(
            phone_number=data.phone_number,
            api_id=data.api_id,
            api_hash=data.api_hash,
            session_manager=session_manager
        )
        result = await tg.sign_in(
            code=data.code,
            phone_code_hash=data.phone_code_hash,
            password=data.password  # передаем пароль, если он есть
        )

        if result["status"] == "ok":
            return {"status": "ok", "message": "Successfully signed in"}
        else:
            raise HTTPException(status_code=400, detail="Failed to verify code")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying code: {str(e)}")