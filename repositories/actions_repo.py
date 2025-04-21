from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Actions
from schema_pydantic.schema_actions import ActionCreate


async def create_action(db: AsyncSession, action_data: ActionCreate) -> Actions:
    new_action = Actions(**action_data.model_dump())
    db.add(new_action)
    await db.commit()
    await db.refresh(new_action)
    return new_action


async def get_all_actions(db: AsyncSession) -> list[Actions]:
    result = await db.execute(select(Actions))
    return result.scalars().all()


async def get_action_by_id(db: AsyncSession, action_id: int) -> Actions | None:
    result = await db.execute(select(Actions).where(Actions.id == action_id))
    return result.scalar_one_or_none()


async def delete_action(db: AsyncSession, action: Actions):
    await db.delete(action)
    await db.commit()


async def update_action(
    db: AsyncSession, existing_action: Actions, new_data: ActionCreate
) -> Actions:
    for key, value in new_data.model_dump().items():
        setattr(existing_action, key, value)
    await db.commit()
    await db.refresh(existing_action)
    return existing_action