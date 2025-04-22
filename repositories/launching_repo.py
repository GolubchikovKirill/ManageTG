from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import BaseActions


async def get_action_by_id(db: AsyncSession, action_id: int) -> BaseActions | None:
    result = await db.execute(select(BaseActions).where(BaseActions.id == action_id))
    return result.scalars().first()