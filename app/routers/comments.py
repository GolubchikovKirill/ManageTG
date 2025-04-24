from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.repositories.comments import (
    create_comment_action,
    get_all_comment_actions,
    get_comment_action_by_id,
    update_comment_action,
    delete_comment_action
)
from app.schemas.comments import CommentActionCreate, CommentActionResponse
from app.services.commenting_logic import BotActionExecutor
from app.services.openai import OpenAIService

router = APIRouter(prefix="/commenting", tags=["Commenting"])


@router.post("/execute-action")
async def execute_comment_action(
    action_id: int,
    api_id: str,
    api_hash: str,
    db: AsyncSession = Depends(get_db)
):
    action = await get_comment_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Comment action not found")

    openai_service = OpenAIService()
    executor = BotActionExecutor(session=db, openai_service=openai_service)
    await executor.run(action=action, api_id=api_id, api_hash=api_hash)

    return {"message": "Comment action executed successfully"}


@router.post("/", response_model=CommentActionResponse)
async def create_action(
    action: CommentActionCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_comment_action(db, action)


@router.get("/", response_model=list[CommentActionResponse])
async def get_all_actions(db: AsyncSession = Depends(get_db)):
    return await get_all_comment_actions(db)


@router.get("/{action_id}", response_model=CommentActionResponse)
async def get_action(action_id: int, db: AsyncSession = Depends(get_db)):
    action = await get_comment_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Comment action not found")
    return action


@router.put("/{action_id}", response_model=CommentActionResponse)
async def update_action(
    action_id: int,
    updated_action: CommentActionCreate,
    db: AsyncSession = Depends(get_db)
):
    action = await update_comment_action(db, action_id, updated_action)
    if not action:
        raise HTTPException(status_code=404, detail="Comment action not found")
    return action


@router.delete("/{action_id}", response_model=CommentActionResponse)
async def delete_action(action_id: int, db: AsyncSession = Depends(get_db)):
    action = await get_comment_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Comment action not found")

    await delete_comment_action(db, action_id)
    return action