from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.accounts import AccountCreate, AccountUpdate, AccountRead
from app.repositories.accounts import (
    create_account_repo,
    get_all_accounts_repo,
    get_account_by_id_repo,
    update_account_repo,
    delete_account_repo
)

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/", response_model=AccountRead)
async def create_account(account: AccountCreate, db: AsyncSession = Depends(get_db)):
    return await create_account_repo(db, account)


@router.get("/", response_model=list[AccountRead])
async def get_all_accounts(db: AsyncSession = Depends(get_db)):
    return await get_all_accounts_repo(db)


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await get_account_by_id_repo(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")
    return account


@router.put("/{account_id}", response_model=AccountRead)
async def update_account(account_id: int, update_data: AccountUpdate, db: AsyncSession = Depends(get_db)):
    account = await update_account_repo(db, account_id, update_data)
    if not account:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")
    return account


@router.delete("/{account_id}")
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_account_repo(db, account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Аккаунт не найден")
    return {"detail": "Аккаунт успешно удален"}
