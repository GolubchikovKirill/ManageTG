import uvicorn
from fastapi import FastAPI
from routers import routers

app = FastAPI()
for routers in routers:
    app.include_router(routers)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
