# backend/app/db.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import settings

# Create engine and async session maker
async_engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
async_session_maker = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()
