from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel


class MessageCreate(BaseModel):
    """Model for creating a new message."""

    conversation_id: str
    role: Literal["user", "assistant"]
    content: str
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Response model for message."""

    id: str
    conversation_id: str
    role: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
