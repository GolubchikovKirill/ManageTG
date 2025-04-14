from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.telegram_auth import TelegramAuth
from database.database import get_db
from database.models import Accounts

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
    phone_number: str  # Добавлено поле phone_number
    code: str
    phone_code_hash: str
    password: str = None

@router.post("/send-code")
async def send_code(data: SendCodeRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Создаем или обновляем аккаунт с api_id и api_hash
        account = await db.execute(select(Accounts).where(Accounts.phone_number == data.phone_number))
        account = account.scalars().first()

        if account:
            account.api_id = data.api_id
            account.api_hash = data.api_hash
            account.proxy_id = data.proxy_id
        else:
            new_account = Accounts(
                phone_number=data.phone_number,
                api_id=data.api_id,
                api_hash=data.api_hash,
                status=True,
                name="",
                last_name="",
                proxy_id=data.proxy_id,
            )
            db.add(new_account)

        await db.commit()

        tg = TelegramAuth(
            phone_number=data.phone_number,
            api_id=data.api_id,
            api_hash=data.api_hash
        )
        result = await tg.send_code()

        if result["status"] == "ok":
            return {"status": "ok", "phone_code_hash": result["phone_code_hash"]}
        else:
            raise HTTPException(status_code=400, detail="Failed to send code")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error sending code: {str(e)}")

@router.post("/sign-in")
async def sign_in(data: SignInRequest, db: AsyncSession = Depends(get_db)):
    try:
        account = await db.execute(select(Accounts).where(Accounts.phone_number == data.phone_number))
        account = account.scalars().first()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        tg = TelegramAuth(
            phone_number=account.phone_number,
            api_id=account.api_id,
            api_hash=account.api_hash
        )
        result = await tg.sign_in(
            code=data.code,
            phone_code_hash=data.phone_code_hash,
            password=data.password
        )

        if result["status"] == "ok":
            return {"status": "ok", "message": "Successfully signed in"}
        else:
            if "2FA password" in result["message"]:
                return {"status": "2fa_required", "message": "2FA password required"}
            raise HTTPException(status_code=400, detail="Failed to verify code or password")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error signing in: {str(e)}")
