from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.config import settings
from app.schemas.views import ViewActionCreate, ViewActionResponse
from app.services.views import ViewService
from app.repositories.views import (
    create_view_action,
    get_all_view_actions,
    get_view_action_by_id,
    update_view_action,
    delete_view_action,
)

router = APIRouter(prefix="/views", tags=["Views"])


async def run_view_action(
    post_link: str,
    action_time: int,
    sessions_path: str,
    count: int,
    random_percentage: int = 20,
):
    executor = ViewService(
        sessions_path=sessions_path,
        action_time=action_time,
        random_percentage=random_percentage,
    )
    await executor.add_views(
        post_link=post_link,
        session_limit=count,
    )


@router.post("/execute-action")
async def execute_view_action(
    action_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    action = await get_view_action_by_id(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="View action not found")

    # Проверка на наличие поста
    if not action.post_link:
        raise HTTPException(status_code=400, detail="Post link cannot be empty")

    try:
        parts = action.post_link.rstrip('/').split('/')
        chat = parts[-2]
    except IndexError:
        raise HTTPException(status_code=400, detail="Invalid post link format")

    sessions_path = settings.SESSIONS_DIR

    # Запускаем накрутку в фоне
    background_tasks.add_task(
        run_view_action,
        chat=chat,
        action_time=action.action_time,
        sessions_path=sessions_path,
        count=action.count,
        random_percentage=action.random_percentage,
    )

    return {"message": "View action started in background"}


@router.post("/", response_model=ViewActionResponse)
async def create_action(
    action: ViewActionCreate,
    db: AsyncSession = Depends(get_db),
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
    db: AsyncSession = Depends(get_db),
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