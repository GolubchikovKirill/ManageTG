from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Загружаем .env с абсолютным путём
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

class Settings(BaseSettings):
    API_ID: int
    API_HASH: str

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo-0125"
    OPENAI_MAX_RETRIES: int = 2
    OPENAI_TIMEOUT: int = 10

    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

DB_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"