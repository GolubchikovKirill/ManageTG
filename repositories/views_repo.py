from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import ViewActions
from schema_pydantic.schema_views import ViewActionCreate


async def create_view_action(db: AsyncSession, action_data: ViewActionCreate) -> ViewActions:
    new_action = ViewActions(**action_data.model_dump())
    db.add(new_action)
    await db.commit()
    await db.refresh(new_action)
    return new_action


async def get_all_view_actions(db: AsyncSession) -> list[ViewActions]:
    result = await db.execute(select(ViewActions))
    return result.scalars().all()


async def get_view_action_by_id(db: AsyncSession, action_id: int) -> ViewActions | None:
    result = await db.execute(
        select(ViewActions).where(ViewActions.id == action_id)
    )
    return result.scalar_one_or_none()


async def update_view_action(
    db: AsyncSession, action_id: int, updated_data: ViewActionCreate
) -> ViewActions | None:
    action = await get_view_action_by_id(db, action_id)
    if not action:
        return None

    for key, value in updated_data.model_dump().items():
        setattr(action, key, value)

    await db.commit()
    await db.refresh(action)
    return action


async def delete_view_action(db: AsyncSession, action_id: int) -> None:
    action = await get_view_action_by_id(db, action_id)
    if action:
        await db.delete(action)
        await db.commit()