import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship

from src.storage.database import Base


class Conversation(Base):
    """Database model for conversation sessions."""

    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    # Relationship to messages
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
