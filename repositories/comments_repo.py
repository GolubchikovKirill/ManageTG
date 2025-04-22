from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import CommentActions
from schema_pydantic.schema_comment import CommentActionCreate


async def create_comment_action(db: AsyncSession, action_data: CommentActionCreate) -> CommentActions:
    new_action = CommentActions(**action_data.model_dump())
    db.add(new_action)
    await db.commit()
    await db.refresh(new_action)
    return new_action


async def get_all_comment_actions(db: AsyncSession) -> list[CommentActions]:
    result = await db.execute(select(CommentActions))
    return result.scalars().all()


async def get_comment_action_by_id(db: AsyncSession, action_id: int) -> CommentActions | None:
    result = await db.execute(
        select(CommentActions).where(CommentActions.id == action_id)
    )
    return result.scalar_one_or_none()


async def update_comment_action(
    db: AsyncSession, action_id: int, updated_data: CommentActionCreate
) -> CommentActions | None:
    action = await get_comment_action_by_id(db, action_id)
    if not action:
        return None

    for key, value in updated_data.model_dump().items():
        setattr(action, key, value)

    await db.commit()
    await db.refresh(action)
    return action


async def delete_comment_action(db: AsyncSession, action_id: int) -> None:
    action = await get_comment_action_by_id(db, action_id)
    if action:
        await db.delete(action)
        await db.commit()