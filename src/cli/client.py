import os
from typing import Dict, List, Union, Generator

from src.agent.main import generate_conversation_response


class AgentClient:
    """Client for interacting with the perplexity CLI agent."""

    def __init__(self):
        """Initialize the agent client."""
        # Ensure OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable must be set")

    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """Chat with conversation context.

        Args:
            messages: List of previous messages in the conversation
            stream: Whether to stream the response

        Returns:
            AI response (string or generator for streaming)
        """
        return generate_conversation_response(messages, stream=stream)
