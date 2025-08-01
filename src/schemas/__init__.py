"""Pydantic schemas for the Perplexity CLI application."""

from typing import List

from pydantic import BaseModel

from .conversation import ConversationResponse
from .message import MessageCreate, MessageResponse


class ConversationExport(BaseModel):
    """Model for exporting a conversation."""

    session: ConversationResponse
    messages: List[MessageResponse]

    class Config:
        from_attributes = True


__all__ = [
    "ConversationResponse",
    "MessageCreate",
    "MessageResponse",
    "ConversationExport",
]
