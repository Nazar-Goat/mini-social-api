from typing import Literal

from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: Literal["DEV", "PROD"]

    APP_NAME: str
    CORS_ALLOW_ORIGINS: list[str] = ["*"]  # noqa

    APP_PORT: int
    MAIN_DOMAIN: str = "192.168.0.1"

    DOCKERIZED: int = 0

    DB_POSTGRES_HOST: str
    DB_POSTGRES_PORT: int
    DB_POSTGRES_USER: str
    DB_POSTGRES_PASS: str
    DB_POSTGRES_NAME: str

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASS: str
    REDIS_AUTH_DB: str
    REDIS_THROTTLING_DB: str
    REDIS_QUEUE_DB: str

    SECRET_KEY: str
    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FAILED_LOGIN_ATTEMPTS: int
    FAILED_LOGIN_ATTEMPTS_TIMEOUT: int

    REFRESH_TTL_DAYS: int
    ACCESS_TTL_MINUTES: int
    ACCESS_COOKIE_NAME: str = "access_token"
    REFRESH_COOKIE_NAME: str = "refresh_token"

    IS_LAX_COOKIE: bool = True
    IS_SECURE_COOKIE: bool = True

    COOKIE_DOMAIN_LIST: list[str] = None

    @property
    def COOKIE_DOMAINS(self):
        if self.COOKIE_DOMAIN_LIST is None:
            return [None]
        return self.COOKIE_DOMAIN_LIST

    @property
    def DATABASE_URI(self):
        return (
            f"postgresql+asyncpg://{self.DB_POSTGRES_USER}:{self.DB_POSTGRES_PASS}@"
            f"{self.DB_POSTGRES_HOST}:{self.DB_POSTGRES_PORT}/{self.DB_POSTGRES_NAME}"
        )

    model_config = SettingsConfigDict(env_file=find_dotenv())


settings = Settings()  # noqa
