from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Proxy, Accounts


async def get_proxy_by_id(db: AsyncSession, proxy_id: int) -> Proxy | None:
    return await db.get(Proxy, proxy_id)


async def get_account_by_phone(db: AsyncSession, phone_number: str) -> Accounts | None:
    result = await db.execute(
        select(Accounts).where(Accounts.phone_number == phone_number)
    )
    return result.scalar_one_or_none()


async def save_account(
    db: AsyncSession,
    phone_number: str,
    api_id: int,
    api_hash: str,
    proxy_id: int
) -> Accounts:
    account = await get_account_by_phone(db, phone_number)

    if account:
        account.api_id = api_id
        account.api_hash = api_hash
        account.proxy_id = proxy_id
        account.is_authorized = True
    else:
        account = Accounts(
            phone_number=phone_number,
            api_id=api_id,
            api_hash=api_hash,
            proxy_id=proxy_id,
            is_authorized=True
        )
        db.add(account)

    return account