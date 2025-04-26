from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
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
async def get_comment_action_by_id_endpoint(
    action_id: int,
    db: AsyncSession = Depends(get_db)
):
    action = await get_comment_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Comment action not found")
    return action

@router.put("/{action_id}", response_model=CommentActionResponse)
async def update_comment_action_endpoint(
    action_id: int,
    action: CommentActionCreate,
    db: AsyncSession = Depends(get_db)
):
    existing_action = await get_comment_action_by_id(db, action_id)
    if not existing_action:
        raise HTTPException(status_code=404, detail="Comment action not found")

    return await update_comment_action(db, action_id, action)

@router.delete("/{action_id}")
async def delete_comment_action_endpoint(
    action_id: int,
    db: AsyncSession = Depends(get_db)
):
    existing_action = await get_comment_action_by_id(db, action_id)
    if not existing_action:
        raise HTTPException(status_code=404, detail="Comment action not found")

    await delete_comment_action(db, action_id)
    return {"message": f"Comment action with ID {action_id} deleted successfully"}


@router.post("/execute/{action_type}")
async def execute_comment_action(
        action_id: int,
        action_type: str,
        api_id: str,
        api_hash: str,
        db: AsyncSession = Depends(get_db)
):
    action = await get_comment_action_by_id(db, action_id)
    if not action:
        raise HTTPException(404, "Действие не найдено")

    valid_types = ["positive", "neutral", "critical", "question"]
    if action_type not in valid_types:
        raise HTTPException(400, f"Недопустимый тип: {action_type}")

    count = getattr(action, f"{action_type}_count", 0)
    if count <= 0:
        raise HTTPException(400, "Нет комментариев для отправки")

    executor = BotActionExecutor(
        session=db,
        openai_service=OpenAIService()
    )

    await executor.run(
        action=action,
        api_id=api_id,
        api_hash=api_hash,
        count=count,
        action_type=action_type
    )

    return {"message": f"Отправлено {count} комментариев типа {action_type}"}