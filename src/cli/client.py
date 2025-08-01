import os
from typing import Dict, Generator, List, Union

from src.agent.main import generate_conversation_response
from src.agent.search_agent import SearchAgent


class AgentClient:
    """Client for interacting with the perplexity CLI agent."""

    def __init__(self):
        """Initialize the agent client."""
        # Ensure OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable must be set")

        # Initialize search agent (only if SERPAPI_KEY is available)
        self.search_agent = None
        if os.getenv("SERPAPI_KEY"):
            try:
                self.search_agent = SearchAgent()
            except Exception as e:
                print(f"Warning: Could not initialize search agent: {e}")

    def chat(
        self, messages: List[Dict[str, str]], stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """Chat with conversation context and internet search.

        Args:
            messages: List of previous messages in the conversation
            stream: Whether to stream the response

        Returns:
            AI response based on internet search and conversation context
        """
        # Use search agent if available
        if self.search_agent and messages:
            # Get the latest user message for search query
            user_messages = [msg for msg in messages if msg.get("role") == "user"]
            if user_messages:
                latest_query = user_messages[-1].get("content", "")
                if latest_query.strip():
                    # Pass full conversation history to search agent
                    return self.search_agent.search_and_answer_with_context(messages, latest_query, stream=stream)

        # Fallback to regular conversation if no search agent or no user message
        return generate_conversation_response(messages, stream=stream)
