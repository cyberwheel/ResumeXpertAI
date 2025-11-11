import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./resumexpert.db"
    ADMIN_PASSWORD: str = os.environ.get("ADMIN_PASSWORD", "changeme")
    UPLOAD_DIR: str = "./uploads"
    PDF_DIR: str = "./generated"
    AI_ENABLED: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
