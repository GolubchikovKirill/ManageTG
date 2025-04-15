from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pyrogram import errors

from database.database import get_db
from database.models import Accounts, Proxy
from services.telegram_auth import TelegramAuth

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


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
    phone_code_hash: str
    password: str = None


def prepare_proxy_config(proxy: Proxy) -> dict:
    """Формирует конфиг прокси для Pyrogram"""
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
    try:
        # Получаем прокси
        proxy = await db.get(Proxy, data.proxy_id)
        if not proxy:
            raise HTTPException(status_code=404, detail="Proxy not found")

        # Инициализация клиента
        tg = TelegramAuth(
            phone_number=data.phone_number,
            api_id=data.api_id,
            api_hash=data.api_hash,
            proxy=prepare_proxy_config(proxy)
        )

        # Отправка кода
        result = await tg.send_code()

        if result["status"] != "ok":
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Failed to send code")
            )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending code: {str(e)}"
        )


@router.post("/sign-in")
async def sign_in(data: SignInRequest, db: AsyncSession = Depends(get_db)):
    try:
        proxy = await db.get(Proxy, data.proxy_id)
        proxy_config = prepare_proxy_config(proxy)

        tg = TelegramAuth(
            phone_number=data.phone_number,
            api_id=data.api_id,
            api_hash=data.api_hash,
            proxy=proxy_config
        )

        result = await tg.sign_in(
            code=data.code,
            phone_code_hash=data.phone_code_hash,
            password=data.password
        )

        if result["status"] != "ok":
            error_msg = result.get("message", "Authentication failed")
            if "2FA" in error_msg:
                return {"status": "2fa_required", "message": error_msg}
            raise HTTPException(status_code=400, detail=error_msg)

        account = await db.scalar(
            select(Accounts).where(Accounts.phone_number == data.phone_number)
        )

        if not account:
            account = Accounts(
                phone_number=data.phone_number,
                api_id=data.api_id,
                api_hash=data.api_hash,
                proxy_id=data.proxy_id,
                is_authorized=True
            )
            db.add(account)
        else:
            account.api_id = data.api_id
            account.api_hash = data.api_hash
            account.proxy_id = data.proxy_id
            account.is_authorized = True

        await db.commit()
        return {"status": "ok", "message": "Successfully signed in"}

    except errors.SessionPasswordNeeded:
        return {"status": "2fa_required", "message": "2FA password required"}
    except errors.PhoneCodeInvalid:
        raise HTTPException(400, "Invalid code")
    except errors.PhoneCodeExpired:
        raise HTTPException(400, "Code expired")
    except errors.PasswordHashInvalid:
        raise HTTPException(400, "Invalid 2FA password")
    except errors.PhoneNumberFlood:
        raise HTTPException(429, "Too many attempts, try later")

    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Authentication error: {str(e)}")