from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME : str = "Mini Sicial API"

    DB_HOST : str
    DB_PORT : str
    DB_USER : str
    DB_PASS : str
    DB_NAME : str

    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int

    @property
    def database_url(self) -> str: #noqa
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
@lru_cache()
def get_settings() -> Settings:
    return Settings()
    