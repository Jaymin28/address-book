"""
SQLAlchemy ORM models.
"""

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from database.session import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    street = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

