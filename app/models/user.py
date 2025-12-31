"""Auto-generated model for User."""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Time, Text, JSON, LargeBinary, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid


class User(Base):
    """SQLAlchemy model for User."""
    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
