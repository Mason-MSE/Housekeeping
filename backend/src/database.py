# database.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory (backend folder)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path, override=True)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator

# Import Base from model package to avoid circular imports
from model.Base import Base

# Database configuration using environment variables
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rootpassword")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "housekeeping")

class DatabaseManager:
    """Manages database engine and session lifecycle."""
    @staticmethod
    def create_engine_and_session():
        """Create and return the SQLAlchemy engine and session factory."""
        url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

        engine = create_engine(
            url,
            echo=True
        )

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine, SessionLocal

# Create engine and session
engine, SessionLocal = DatabaseManager.create_engine_and_session()

# Dependency for FastAPI
def get_db() -> Generator:
    """FastAPI dependency that yields a database session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
