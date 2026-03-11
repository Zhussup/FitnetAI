"""
Конфигурация подключения к базам данных
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import SQLITE_URL, POSTGRES_URL

# SQLite (основная база)
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)

# PostgreSQL (резервная база)
postgres_engine = create_engine(POSTGRES_URL)
PostgresSession = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)

Base = declarative_base()

def get_db():
    """Dependency для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
