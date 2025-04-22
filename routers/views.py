from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schema_pydantic.schema_views import ViewActionCreate, ViewActionResponse
from services import openai_service
from services.commenting_logic import BotActionExecutor
from repositories.views_repo import (
    create_view_action,
    get_all_view_actions,
    get_view_action_by_id,
    update_view_action,
    delete_view_action
)

router = APIRouter(prefix="/views", tags=["Views"])


@router.post("/execute-action")
async def execute_view_action(
    action_id: int,
    api_id: str,
    api_hash: str,
    db: AsyncSession = Depends(get_db)
):
    action = await get_view_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="View action not found")

    executor = BotActionExecutor(session=db, openai_service=openai_service)
    await executor.run(action=action, api_id=api_id, api_hash=api_hash)

    return {"message": "View action executed successfully"}


@router.post("/", response_model=ViewActionResponse)
async def create_action(
    action: ViewActionCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_view_action(db, action)


@router.get("/", response_model=list[ViewActionResponse])
async def get_all_actions(db: AsyncSession = Depends(get_db)):
    return await get_all_view_actions(db)


@router.get("/{action_id}", response_model=ViewActionResponse)
async def get_action(action_id: int, db: AsyncSession = Depends(get_db)):
    action = await get_view_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="View action not found")
    return action


@router.put("/{action_id}", response_model=ViewActionResponse)
async def update_action(
    action_id: int,
    updated_action: ViewActionCreate,
    db: AsyncSession = Depends(get_db)
):
    action = await update_view_action(db, action_id, updated_action)
    if not action:
        raise HTTPException(status_code=404, detail="View action not found")
    return action


@router.delete("/{action_id}", response_model=ViewActionResponse)
async def delete_action(action_id: int, db: AsyncSession = Depends(get_db)):
    action = await get_view_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="View action not found")

    await delete_view_action(db, action_id)
    return action