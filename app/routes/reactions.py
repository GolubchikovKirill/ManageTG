from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.reaction import ReactionActionCreate, ReactionActionResponse
from app.services.reactions import ReactionService
from app.repositories.reactions import (
    create_reaction_action,
    get_all_reaction_actions,
    get_reaction_action_by_id,
    update_reaction_action,
    delete_reaction_action,
)

router = APIRouter(prefix="/reactions", tags=["Reactions"])

SESSIONS_PATH = "session"

@router.post("/execute-action")
async def execute_reaction_action(
    action_id: int,
    db: AsyncSession = Depends(get_db)
):
    action = await get_reaction_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Reaction action not found")

    service = ReactionService(sessions_path=SESSIONS_PATH)
    await service.react_to_last_posts(
        channel_id=action.channel_id,
        emoji=action.emoji,
        max_sessions=action.count
    )
    return {"message": "Reaction action executed successfully"}


@router.post("/", response_model=ReactionActionResponse)
async def create_action(action: ReactionActionCreate, db: AsyncSession = Depends(get_db)):
    return await create_reaction_action(db, action)


@router.get("/", response_model=list[ReactionActionResponse])
async def get_all_actions(db: AsyncSession = Depends(get_db)):
    return await get_all_reaction_actions(db)


@router.get("/{action_id}", response_model=ReactionActionResponse)
async def get_action(action_id: int, db: AsyncSession = Depends(get_db)):
    action = await get_reaction_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Reaction action not found")
    return action


@router.put("/{action_id}", response_model=ReactionActionResponse)
async def update_action(
    action_id: int,
    updated_action: ReactionActionCreate,
    db: AsyncSession = Depends(get_db)
):
    action = await update_reaction_action(db, action_id, updated_action)
    if not action:
        raise HTTPException(status_code=404, detail="Reaction action not found")
    return action


@router.delete("/{action_id}", response_model=ReactionActionResponse)
async def delete_action(action_id: int, db: AsyncSession = Depends(get_db)):
    action = await get_reaction_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Reaction action not found")

    await delete_reaction_action(db, action_id)
    return action