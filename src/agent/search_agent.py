"""Intelligent search agent that uses tool calling for internet searches."""

from typing import Generator, Union

from src.agent.llm import generate_llm_response
from src.tools import ToolExecutor


class SearchAgent:
    """Intelligent agent that uses tool calling to search the internet."""

    def __init__(self):
        """Initialize the search agent."""
        self.tool_executor = ToolExecutor()

    def search_and_answer(
        self, query: str, stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """Complete search and answer pipeline using tool calling.

        Args:
            query: User's question/query
            stream: Whether to stream the response

        Returns:
            Comprehensive answer based on internet search via tool calling
        """
        # Create system prompt for the search agent
        system_prompt = """You are an intelligent search assistant with access to internet search tools.

When a user asks a question:
1. Use the search_internet tool to find current, relevant information
2. You may need to make multiple searches with different queries to gather comprehensive information
3. After gathering search results, provide a detailed, accurate answer
4. Include specific facts, numbers, and details when available
5. Be objective and mention sources when helpful
6. Write in a natural, conversational tone

Always use the search tool first before providing your final answer."""

        # Create conversation with the user query
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        # Get available tools
        tools = self.tool_executor.get_available_tools()

        # Generate response with tool calling
        return generate_llm_response(
            input=messages,
            tools=tools,
            stream=stream,
            temperature=0
        )
