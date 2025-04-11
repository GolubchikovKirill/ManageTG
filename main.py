import uvicorn
from fastapi import FastAPI
from routers.auth import router as auth_router
from routers.control import router as session_router
from routers.сommenting import router as commenting
from routers.channels import router as channels_router
app = FastAPI()
app.include_router(auth_router)
app.include_router(session_router, prefix="/session", tags=["session"])
app.include_router(commenting, prefix="/start", tags=["start"])
app.include_router(channels_router, prefix="/channels", tags=["channels"])





if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)