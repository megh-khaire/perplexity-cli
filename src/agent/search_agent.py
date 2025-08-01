"""Intelligent search agent that uses tool calling for internet searches."""

from typing import Generator, Union

from src.agent.prompt import load_prompt
from src.agent.llm import generate_llm_response
from src.tools import ToolExecutor


class SearchAgent:
    """Intelligent agent that uses tool calling to search the internet."""

    def __init__(self):
        """Initialize the search agent."""
        self.tool_executor = ToolExecutor()

    def search_and_answer_with_context(
        self, conversation_history: list, query: str, stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """Complete search and answer pipeline with conversation context.

        Args:
            conversation_history: Full conversation history
            query: Latest user question/query
            stream: Whether to stream the response

        Returns:
            Comprehensive answer based on internet search and conversation context
        """
        # Create system prompt for the search agent
        system_prompt = load_prompt("search_and_answer")["system"]

        # Build messages with conversation context
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history (but limit to recent messages to avoid token limit)
        recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        messages.extend(recent_history)

        # Get available tools
        tools = self.tool_executor.get_available_tools()

        # Generate response with tool calling
        return generate_llm_response(
            input=messages, tools=tools, stream=stream, temperature=0
        )
