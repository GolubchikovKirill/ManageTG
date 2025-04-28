from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import ReactionActions
from app.schemas.reaction import ReactionActionCreate


async def create_reaction_action(db: AsyncSession, action_data: ReactionActionCreate) -> ReactionActions:
    action = ReactionActions(**action_data.model_dump())
    db.add(action)
    await db.commit()
    await db.refresh(action)
    return action


async def get_all_reaction_actions(db: AsyncSession) -> list[ReactionActions]:
    result = await db.execute(select(ReactionActions))
    return result.scalars().all()


async def get_reaction_action_by_id(db: AsyncSession, action_id: int) -> ReactionActions | None:
    result = await db.execute(select(ReactionActions).where(ReactionActions.id == action_id))
    return result.scalars().first()


async def update_reaction_action(db: AsyncSession, action_id: int, updated_data: ReactionActionCreate) -> ReactionActions | None:
    action = await get_reaction_action_by_id(db, action_id)
    if not action:
        return None

    for key, value in updated_data.model_dump().items():
        setattr(action, key, value)

    await db.commit()
    await db.refresh(action)
    return action


async def delete_reaction_action(db: AsyncSession, action_id: int) -> None:
    action = await get_reaction_action_by_id(db, action_id)
    if action:
        await db.delete(action)
        await db.commit()