"""Auto-generated model for Post."""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Time, Text, JSON, LargeBinary, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid


class Post(Base):
    """SQLAlchemy model for Post."""
    __tablename__ = "posts"

    id = Column(UUID, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    published = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    user = relationship("User", back_populates="posts")
