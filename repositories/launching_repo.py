from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Actions


async def get_action_by_id(db: AsyncSession, action_id: int) -> Actions | None:
    result = await db.execute(select(Actions).where(Actions.id == action_id))
    return result.scalars().first()