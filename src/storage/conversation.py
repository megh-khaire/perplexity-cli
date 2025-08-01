"""Conversation storage operations."""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import desc

from src.models import Conversation, Message
from src.schemas import (
    ConversationExport,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from src.storage.database import get_database_session


class ConversationStorage:
    """Handles all conversation storage operations."""

    def create_conversation(self, title: Optional[str] = None) -> ConversationResponse:
        """Create a new conversation session."""
        if not title:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        with get_database_session() as session:
            conversation = Conversation(title=title)
            session.add(conversation)
            session.flush()

            return ConversationResponse(
                id=conversation.id,
                title=conversation.title,
                created_at=conversation.created_at,
                last_accessed=conversation.last_accessed,
            )

    def get_conversation(self, conversation_id: str) -> Optional[ConversationResponse]:
        """Get a conversation by ID."""
        with get_database_session() as session:
            conversation = (
                session.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )

            if not conversation:
                return None

            return ConversationResponse(
                id=conversation.id,
                title=conversation.title,
                created_at=conversation.created_at,
                last_accessed=conversation.last_accessed,
            )

    def list_conversations(self, limit: int = 10) -> List[ConversationResponse]:
        """List all conversations, most recent first."""
        with get_database_session() as session:
            conversations = (
                session.query(Conversation)
                .order_by(desc(Conversation.last_accessed))
                .limit(limit)
                .all()
            )

            result = []
            for conv in conversations:
                result.append(
                    ConversationResponse(
                        id=conv.id,
                        title=conv.title,
                        created_at=conv.created_at,
                        last_accessed=conv.last_accessed,
                    )
                )

            return result

    def update_conversation_access(self, conversation_id: str) -> None:
        """Update the last accessed time for a conversation."""
        with get_database_session() as session:
            conversation = (
                session.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )

            if conversation:
                conversation.last_accessed = datetime.utcnow()

    def update_conversation_title(self, conversation_id: str, title: str) -> None:
        """Update the title of a conversation."""
        with get_database_session() as session:
            conversation = (
                session.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )

            if conversation:
                conversation.title = title[:255] if len(title) > 255 else title

    def add_message(self, message_data: MessageCreate) -> MessageResponse:
        """Add a message to a conversation."""
        with get_database_session() as session:
            self.update_conversation_access(message_data.conversation_id)

            message = Message(
                conversation_id=message_data.conversation_id,
                role=message_data.role,
                content=message_data.content,
                meta_data=message_data.metadata,
            )
            session.add(message)
            session.flush()

            return MessageResponse(
                id=message.id,
                conversation_id=message.conversation_id,
                role=message.role,
                content=message.content,
                timestamp=message.timestamp,
                metadata=message.meta_data,
            )

    def get_conversation_messages(
        self, conversation_id: str, limit: Optional[int] = None
    ) -> List[MessageResponse]:
        """Get all messages for a conversation."""
        with get_database_session() as session:
            query = (
                session.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(desc(Message.timestamp))
            )

            if limit:
                query = query.limit(limit)

            messages = query.all()

            return [
                MessageResponse(
                    id=msg.id,
                    conversation_id=msg.conversation_id,
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    metadata=msg.meta_data,
                )
                for msg in messages
            ]

    def get_conversation_history(
        self, conversation_id: str, message_limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Get conversation history in OpenAI chat format."""
        messages = self.get_conversation_messages(conversation_id, message_limit)
        messages.reverse()

        history = []
        for msg in messages:
            history.append({"role": msg.role, "content": msg.content})

        return history

    def export_conversation(self, conversation_id: str) -> Optional[ConversationExport]:
        """Export a complete conversation with all messages."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None

        messages = self.get_conversation_messages(conversation_id)

        return ConversationExport(session=conversation, messages=messages)

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages."""
        with get_database_session() as session:
            conversation = (
                session.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )

            if not conversation:
                return False

            session.delete(conversation)  # Cascade will delete messages
            return True

    def clear_all_conversations(self) -> int:
        """Delete all conversations and messages. Returns count of deleted conversations."""
        with get_database_session() as session:
            count = session.query(Conversation).count()
            session.query(Message).delete()
            session.query(Conversation).delete()
            return count

    def search_conversations(
        self, query: str, limit: int = 20
    ) -> List[ConversationResponse]:
        """Search conversations by title or message content."""
        with get_database_session() as session:
            # Search in conversation titles and message content
            conversations = (
                session.query(Conversation)
                .filter(Conversation.title.contains(query))
                .order_by(desc(Conversation.last_accessed))
                .limit(limit)
                .all()
            )

            # Also search in message content
            message_conversations = (
                session.query(Conversation)
                .join(Message)
                .filter(Message.content.contains(query))
                .order_by(desc(Conversation.last_accessed))
                .limit(limit)
                .all()
            )

            # Combine and deduplicate
            all_conversations = {
                conv.id: conv for conv in conversations + message_conversations
            }

            result = []
            for conv in all_conversations.values():
                result.append(
                    ConversationResponse(
                        id=conv.id,
                        title=conv.title,
                        created_at=conv.created_at,
                        last_accessed=conv.last_accessed,
                    )
                )

            # Sort by last accessed
            result.sort(key=lambda x: x.last_accessed, reverse=True)
            return result[:limit]
