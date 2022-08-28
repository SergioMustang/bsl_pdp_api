import os
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    # Load .env file

    PROJECT_NAME: str = os.getenv('PROJECT_NAME')
    PROJECT_URL_PREFIX: str = os.getenv('PROJECT_URL_PREFIX')
    DEBUG: bool = os.getenv('DEBUG')
    SERVICE_HOST: str = os.getenv('SERVICE_HOST')
    SERVICE_PORT: str = os.getenv('SERVICE_PORT')

    TIME_ZONE: str = 'Europe/Moscow'
    TOKEN_URL: str = os.getenv('TOKEN_URL')
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # JWT
    JWT_SECRET: str = os.getenv('JWT_SECRET', 'secret')
    JWT_ACCESS_EXPIRE_MINUTES: int = os.getenv('JWT_ACCESS_EXPIRE_MINUTES', 15)
    JWT_REFRESH_EXPIRE_MINUTES: int = os.getenv('JWT_REFRESH_EXPIRE_MINUTES', 30 * 60 * 24)
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', 'HS256')

    class Config:
        case_sensitive = True


settings = Settings()
