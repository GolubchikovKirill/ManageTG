from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database import get_db
from services.openai_service import OpenAIService
from database.models import Actions
from services.commenting_logic import BotActionExecutor

router = APIRouter(
    prefix="/launching_actions",
    tags=["launching_actions"],
)


# Роут для выполнения действия бота
@router.post("/execute-action")
async def execute_bot_action(
        action_id: int,
        api_id: str,
        api_hash: str,
        db: AsyncSession = Depends(get_db)
):
    """
    Запуск действия для всех сессий (комментарий, реакция, просмотр).
    """
    # Получаем действие из базы данных
    result = await db.execute(select(Actions).where(Actions.id == action_id))
    action = result.scalars().first()

    if not action:
        return {"error": "Action not found"}

    # Создаем сервис для генерации комментариев
    openai_service = OpenAIService()

    # Создаем объект для выполнения действий
    bot_executor = BotActionExecutor(session=db, openai_service=openai_service)

    # Запускаем выполнение действия для всех сессий
    await bot_executor.run(action=action, api_id=api_id, api_hash=api_hash)

    return {"message": "Action executed successfully"}
