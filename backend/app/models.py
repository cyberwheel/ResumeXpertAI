# backend/app/models.py
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    html = Column(Text, nullable=False)
    css = Column(Text, nullable=True)
    requires_photo = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True)
    data = Column(JSON)
    pdf_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
