import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.database.database import create_tables
from app.routers import routers

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

# async def startup():
#     await create_tables()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)