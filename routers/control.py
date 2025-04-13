from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.session_control import SessionManager
from services.openai_service import OpenAIService
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from services.start_commenting import BotActionExecutor
from sqlalchemy import select
from database.models import Actions

router = APIRouter()

session_manager = SessionManager()
openai_service = OpenAIService()


# Модели для запроса
class SessionRequest(BaseModel):
    phone_number: str
    api_id: int
    api_hash: str


class CommentRequest(BaseModel):
    phone_number: str
    code: str


# Роут для создания сессии
@router.post("/sessions/create")
async def create_session(request: SessionRequest):
    try:
        # Создаем сессию
        client = session_manager.create_session(request.phone_number, request.api_id, request.api_hash)

        # Асинхронно запускаем клиент
        await client.start()
        await client.stop()  # После успешного подключения сразу остановим клиент

        return {"status": "session_created", "phone_number": request.phone_number}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


# Роут для получения сессии
@router.get("/sessions/{phone_number}")
async def get_session(phone_number: str, request: SessionRequest):
    try:
        # Получаем сессию
        client = await session_manager.get_session(phone_number, request.api_id, request.api_hash)

        # Проверяем подключение
        if not client.is_connected():
            await client.start()  # Если клиент не подключен, подключаем его
        return {"status": "session_loaded", "phone_number": phone_number}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session for {phone_number} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading session: {str(e)}")


# Роут для удаления сессии
@router.delete("/sessions/{phone_number}")
async def delete_session(phone_number: str):
    try:
        await session_manager.delete_session(phone_number)
        return {"status": "session_deleted", "phone_number": phone_number}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session for {phone_number} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


# Роут для генерации имени
@router.get("/generate-name")
async def generate_name():
    try:
        name = await openai_service.generate_name()
        return {"name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating name: {str(e)}")


# Роут для генерации комментария
@router.get("/generate-comment")
async def generate_comment():
    try:
        comment = await openai_service.generate_comment()
        return {"comment": comment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating comment: {str(e)}")


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
    # Получаем действие из базы данных (асинхронно)
    result = await db.execute(select(Actions).where(Actions.id == action_id))
    action = result.scalars().first()

    if not action:
        return {"error": "Action not found"}

    # Создаем объект для выполнения действий
    bot_executor = BotActionExecutor(session=db, openai_service=openai_service)

    # Запускаем выполнение действия для всех сессий
    await bot_executor.run(action=action, api_id=api_id, api_hash=api_hash)

    return {"message": "Action executed successfully"}