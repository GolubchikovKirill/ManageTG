from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from app.core.db import get_db
from app.models.models import Proxy
from app.services.telegram_auth import TelegramAuth
from app.schemas.auth import SendCodeRequest, SignInRequest
from app.repositories.auth import get_proxy_by_id, save_account

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# In-memory менеджер для хранения авторизаций (в проде — Redis или БД, в идеале)
class AuthManager:
    _store: Dict[str, Dict] = {}

    @classmethod
    def save(cls, phone_number: str, auth_obj: TelegramAuth, phone_code_hash: str):
        cls._store[phone_number] = {
            "auth": auth_obj,
            "hash": phone_code_hash
        }

    @classmethod
    def get(cls, phone_number: str):
        return cls._store.get(phone_number)

    @classmethod
    def remove(cls, phone_number: str):
        cls._store.pop(phone_number, None)


def prepare_proxy_config(proxy: Proxy) -> dict | None:
    if not proxy:
        return None
    return {
        "scheme": proxy.type.lower(),
        "hostname": proxy.ip_address,
        "port": proxy.port,
        "username": proxy.login,
        "password": proxy.password
    }


@router.post("/send-code")
async def send_code(data: SendCodeRequest, db: AsyncSession = Depends(get_db)):
    proxy = await get_proxy_by_id(db, data.proxy_id)
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")

    tg = TelegramAuth(
        phone_number=data.phone_number,
        api_id=data.api_id,
        api_hash=data.api_hash,
        proxy=prepare_proxy_config(proxy)
    )

    result = await tg.send_code()
    if result["status"] != "ok":
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to send code"))

    AuthManager.save(data.phone_number, tg, result["phone_code_hash"])
    return {"status": "ok", "message": "Code sent"}


@router.post("/sign-in")
async def sign_in(data: SignInRequest, db: AsyncSession = Depends(get_db)):
    session_data = AuthManager.get(data.phone_number)
    if not session_data:
        raise HTTPException(400, "No auth session found. You must call /send-code first.")

    tg: TelegramAuth = session_data["auth"]

    result = await tg.sign_in(code=data.code, password=data.password)
    if result["status"] != "ok":
        if result["status"] == "2fa_required":
            return result
        raise HTTPException(400, result.get("message", "Authentication failed"))

    AuthManager.remove(data.phone_number)

    try:
        await save_account(
            db=db,
            phone_number=data.phone_number,
            api_id=data.api_id,
            api_hash=data.api_hash,
            proxy_id=data.proxy_id
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Database error: {e}")

    return {"status": "ok", "message": "Successfully signed in"}
