from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.schemas.views import ViewActionCreate, ViewActionResponse
from app.services.views import ViewService
from app.repositories.views import (
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
    db: AsyncSession = Depends(get_db)
):
    action = await get_view_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="View action not found")

    #
    sessions_path = "sessions"
    action_time = 1

    executor = ViewService(sessions_path=sessions_path, action_time=action_time)
    await executor.add_views(post_link=action.post_link)

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