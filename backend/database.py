from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./discord_shop.db")
    secret_key: str = os.getenv("SECRET_KEY", "changeme-dev-only")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    discord_bot_token: str = os.getenv("DISCORD_BOT_TOKEN", "")
    discord_public_key: str = os.getenv("DISCORD_PUBLIC_KEY", "a" * 64)  # dummy for local
    base_url: str = os.getenv("BASE_URL", "http://localhost:8000")

settings = Settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
