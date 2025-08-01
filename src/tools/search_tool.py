"""Search tool for LLM function calling."""

import json
from typing import Any, Dict, List

from src.clients.serp_api import SerpAPIClient


class SearchTool:
    """Tool for performing internet searches via SerpAPI."""

    def __init__(self):
        """Initialize the search tool."""
        self.serp_client = SerpAPIClient()

    @property
    def function_definition(self) -> Dict[str, Any]:
        """Get the OpenAI function definition for this tool."""
        return {
            "name": "search_internet",
            "description": "Search the internet for current information about any topic. Use this when you need up-to-date information, facts, news, or data that you don't have in your training.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find information about",
                    },
                    "search_type": {
                        "type": "string",
                        "enum": ["web", "news"],
                        "description": "Type of search - 'web' for general search, 'news' for recent news",
                        "default": "web",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (1-10)",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        }

    def execute(
        self, query: str, search_type: str = "web", num_results: int = 5
    ) -> str:
        """Execute the search tool.

        Args:
            query: Search query
            search_type: Type of search (web or news)
            num_results: Number of results to return

        Returns:
            JSON string with search results
        """
        try:
            if search_type == "news":
                results = self.serp_client.search_news(query, num_results)
            else:
                results = self.serp_client.search(query, num_results)

            # Format results for the LLM
            search_results = []
            for result in results:
                search_results.append(
                    {
                        "title": result.title,
                        "url": result.link,
                        "snippet": result.snippet,
                        "source": result.source,
                    }
                )

            return json.dumps(
                {
                    "query": query,
                    "search_type": search_type,
                    "num_results": len(search_results),
                    "results": search_results,
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps(
                {
                    "error": f"Search failed: {str(e)}",
                    "query": query,
                    "search_type": search_type,
                }
            )


def get_available_tools() -> List[SearchTool]:
    """Get list of available tools."""
    try:
        return [SearchTool()]
    except Exception as e:
        print(f"Warning: Could not initialize search tool: {e}")
        return []
