"""
Database configuration — SQLite via SQLAlchemy.
"""

from .session import Base, SessionLocal, engine, get_db  # re-export for backwards compatibility
