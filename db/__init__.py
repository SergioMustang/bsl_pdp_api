import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base  # noqa
from dotenv import load_dotenv
from .models import user
from redis import Redis


def get_url():
    load_dotenv()
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    database = os.getenv('DB_NAME')
    return f'postgresql://{user}:{password}@{host}:{port}/{database}'


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_redis_connection():
    return Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))


engine = create_engine(get_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


