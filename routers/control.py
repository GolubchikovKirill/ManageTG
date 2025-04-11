from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.session_control import SessionManager
from services.openai_service import OpenAIService

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
        client = session_manager.create_session(request.phone_number, request.api_id, request.api_hash)
        await client.connect()
        await client.disconnect()
        return {"status": "session_created", "phone_number": request.phone_number}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Роут для получения сессии
@router.get("/sessions/{phone_number}")
async def get_session(phone_number: str, request: SessionRequest):
    try:
        client = session_manager.get_session(phone_number, request.api_id, request.api_hash)
        return {"status": "session_loaded", "phone_number": phone_number}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session for {phone_number} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Роут для удаления сессии
@router.delete("/sessions/{phone_number}")
async def delete_session(phone_number: str):
    try:
        session_manager.delete_session(phone_number)
        return {"status": "session_deleted", "phone_number": phone_number}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session for {phone_number} not found.")

# Роут для генерации имени
@router.get("/generate-name")
async def generate_name():
    try:
        name = openai_service.generate_name()
        return {"name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating name.")

# Роут для генерации комментария
@router.get("/generate-comment")
async def generate_comment():
    try:
        comment = openai_service.generate_comment()
        return {"comment": comment}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating comment.")