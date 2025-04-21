from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Загружаем .env с абсолютным путём
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

class Settings(BaseSettings):
    DB_URL: str
    API_ID: int
    API_HASH: str
    OPENAI_API_KEY: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()