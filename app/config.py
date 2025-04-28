from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field
import os

class Settings(BaseSettings):
    OPENAI_API_KEY: str

    API_ID: int
    API_HASH: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    @computed_field
    @property
    def db_url(self) -> PostgresDsn:
        url = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return str(PostgresDsn(url))

    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), "../.env"))

settings = Settings()
print(settings.db_url)