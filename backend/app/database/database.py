from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

from ..config import get_settings

settings = get_settings()

# Ensure data directory exists
os.makedirs(settings.data_dir, exist_ok=True)

DATABASE_URL = f"sqlite:///{settings.data_dir}/rag_agent.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Document(Base):
    """Uploaded documents table."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    product_count = Column(Integer, default=0)
    status = Column(String, default="processed")
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class ConversationMessage(Base):
    """Conversation history table."""

    __tablename__ = "conversation_messages"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class WhatsAppSession(Base):
    """WhatsApp sessions table."""

    __tablename__ = "whatsapp_sessions"

    id = Column(String, primary_key=True)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    session_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)


class Product(Base):
    """Product catalog table for dynamic data (price, availability)."""

    __tablename__ = "products"

    id = Column(String, primary_key=True)  # composite: name_variant
    product_name = Column(String, nullable=False, index=True)
    variant = Column(String, nullable=True)
    price_lkr = Column(Float, default=0.0)
    available = Column(String, default="Yes")
    image_paths = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """Admin users table."""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
