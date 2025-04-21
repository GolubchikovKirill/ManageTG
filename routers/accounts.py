from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.database import get_db
from database.models import Accounts
from pydantic import BaseModel
from typing import Optional


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


router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/", response_model=AccountRead)
async def create_account(account: AccountCreate, db: AsyncSession = Depends(get_db)):
    new_account = Accounts(**account.model_dump())
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    return new_account


@router.get("/", response_model=list[AccountRead])
async def get_all_accounts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Accounts))
    return result.scalars().all()


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Accounts).where(Accounts.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")
    return account


@router.put("/{account_id}", response_model=AccountRead)
async def update_account(account_id: int, update_data: AccountUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Accounts).where(Accounts.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(account, key, value)

    await db.commit()
    await db.refresh(account)
    return account


@router.delete("/{account_id}")
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Accounts).where(Accounts.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")

    await db.delete(account)
    await db.commit()
    return {"detail": "Аккаунт успешно удален"}