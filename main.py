# import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import create_tables
from routers import routers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)

async def startup():
    await create_tables()

if __name__ == "__main__":
    # asyncio.run(startup())
    uvicorn.run(app, host="0.0.0.0", port=8080)