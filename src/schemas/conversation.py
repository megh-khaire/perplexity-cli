from datetime import datetime

from pydantic import BaseModel


class ConversationResponse(BaseModel):
    """Response model for conversation session."""

    id: str
    title: str
    created_at: datetime
    last_accessed: datetime

    class Config:
        from_attributes = True
