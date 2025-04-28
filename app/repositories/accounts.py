from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List

from app.models.models import Accounts
from app.schemas.accounts import AccountCreate, AccountUpdate


async def create_account_repo(db: AsyncSession, account_data: AccountCreate) -> Accounts:
    new_account = Accounts(**account_data.model_dump())
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    return new_account


async def get_all_accounts_repo(db: AsyncSession) -> List[Accounts]:
    result = await db.execute(select(Accounts))
    return result.scalars().all()


async def get_account_by_id_repo(db: AsyncSession, account_id: int) -> Optional[Accounts]:
    result = await db.execute(select(Accounts).where(Accounts.id == account_id))
    return result.scalar_one_or_none()


async def update_account_repo(db: AsyncSession, account_id: int, update_data: AccountUpdate) -> Optional[Accounts]:
    result = await db.execute(select(Accounts).where(Accounts.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        return None

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(account, key, value)

    await db.commit()
    await db.refresh(account)
    return account


async def delete_account_repo(db: AsyncSession, account_id: int) -> bool:
    result = await db.execute(select(Accounts).where(Accounts.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        return False

    await db.delete(account)
    await db.commit()
    return True