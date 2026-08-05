"""
Database module for PostgreSQL persistence using SQLAlchemy.

Replaces file-based storage with a proper database backend.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Text, Float, Integer, DateTime, JSON, LargeBinary, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from datetime import datetime
from typing import Optional, Dict, Any
import json

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Database availability flag
_db_available = None

# Create SQLAlchemy engine (only if DATABASE_URL is set)
engine = None
SessionLocal = None

if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        print(f"Warning: Failed to create database engine: {e}")
        print("Falling back to file-based storage")
        SessionLocal = None
else:
    print("Warning: DATABASE_URL not set, using file-based storage")

# Base class for models
class Base(DeclarativeBase):
    pass


class RawCaptureDB(Base):
    """SQLAlchemy model for raw captures."""
    __tablename__ = "raw_captures"
    
    id = Column(String, primary_key=True)
    timestamp = Column(String, nullable=False)
    type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=True)
    extra_metadata = Column(JSON, nullable=True, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


class WikiNoteDB(Base):
    """SQLAlchemy model for wiki notes."""
    __tablename__ = "wiki_notes"
    
    id = Column(String, primary_key=True)
    timestamp = Column(String, nullable=False)
    raw_id = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    tags = Column(JSON, nullable=True, default=[])
    summary = Column(Text, nullable=True, default="")
    links = Column(JSON, nullable=True, default={})
    embedding_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmbeddingDB(Base):
    """SQLAlchemy model for embeddings."""
    __tablename__ = "embeddings"
    
    id = Column(String, primary_key=True)  # wiki note ID
    embedding = Column(LargeBinary, nullable=False)  # Stored as binary
    model_name = Column(String, nullable=False, default="BAAI/bge-small-en-v1.5")
    dimension = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def is_db_available() -> bool:
    """
    Check if database is available.
    Returns True if database is connected and working, False otherwise.
    """
    global _db_available
    if _db_available is not None:
        return _db_available
    
    if SessionLocal is None:
        _db_available = False
        return False
    
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        _db_available = True
        return True
    except Exception:
        _db_available = False
        return False


def get_db() -> Session:
    """
    Get database session.
    
    Yields:
        SQLAlchemy session
    """
    if SessionLocal is None:
        raise RuntimeError("Database not available. SessionLocal is None.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables if they don't exist.
    """
    if engine is None:
        print("Database engine not available, skipping initialization")
        return False
    
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized successfully")
        return True
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("Falling back to file-based storage")
        return False


def drop_all_tables():
    """
    Drop all tables (use with caution).
    """
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped")


def reset_db():
    """
    Reset database by dropping and recreating all tables.
    """
    drop_all_tables()
    init_db()


# Helper functions for model conversion
def raw_capture_to_db(raw_capture) -> RawCaptureDB:
    """Convert RawCapture model to DB model."""
    return RawCaptureDB(
        id=raw_capture.id,
        timestamp=raw_capture.timestamp,
        type=raw_capture.type,
        content=raw_capture.content,
        source=raw_capture.source,
        extra_metadata=raw_capture.metadata
    )


def db_to_raw_capture(db_capture: RawCaptureDB):
    """Convert DB model to RawCapture model."""
    from models import RawCapture
    return RawCapture(
        id=db_capture.id,
        timestamp=db_capture.timestamp,
        type=db_capture.type,
        content=db_capture.content,
        source=db_capture.source,
        metadata=db_capture.extra_metadata
    )


def wiki_note_to_db(wiki_note) -> WikiNoteDB:
    """Convert WikiNote model to DB model."""
    return WikiNoteDB(
        id=wiki_note.id,
        timestamp=wiki_note.timestamp,
        raw_id=wiki_note.raw_id,
        content=wiki_note.content,
        category=wiki_note.category,
        tags=wiki_note.tags or [],
        summary=wiki_note.summary or "",
        links=wiki_note.links or {},
        embedding_path=wiki_note.embedding_path
    )


def db_to_wiki_note(db_note: WikiNoteDB):
    """Convert DB model to WikiNote model."""
    from models import WikiNote
    return WikiNote(
        id=db_note.id,
        timestamp=db_note.timestamp,
        raw_id=db_note.raw_id,
        content=db_note.content,
        category=db_note.category,
        tags=db_note.tags or [],
        summary=db_note.summary or "",
        links=db_note.links or {},
        embedding_path=db_note.embedding_path
    )


if __name__ == "__main__":
    # Initialize database
    init_db()

    # Test connection
    if is_db_available():
        print("Database connection successful!")
    else:
        print("Database not available, using file-based storage")
