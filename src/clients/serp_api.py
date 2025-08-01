"""SerpAPI client for internet search functionality."""

import os
from typing import Dict, List, Optional
from serpapi import GoogleSearch


class SearchResult:
    """Represents a search result."""

    def __init__(self, title: str, link: str, snippet: str, source: str = None):
        self.title = title
        self.link = link
        self.snippet = snippet
        self.source = source or link

    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "link": self.link,
            "snippet": self.snippet,
            "source": self.source,
        }


class SerpAPIClient:
    """Client for SerpAPI internet search."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize SerpAPI client."""
        self.api_key = api_key or os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_KEY environment variable must be set")

    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform a Google search using SerpAPI.

        Args:
            query: Search query
            num_results: Number of results to return (max 10 for free tier)

        Returns:
            List of SearchResult objects
        """
        try:
            search = GoogleSearch(
                {
                    "q": query,
                    "api_key": self.api_key,
                    "num": min(num_results, 10),  # SerpAPI free tier limit
                    "gl": "us",  # Country
                    "hl": "en",  # Language
                }
            )

            results = search.get_dict()
            search_results = []

            # Parse organic results
            if "organic_results" in results:
                for result in results["organic_results"]:
                    search_results.append(
                        SearchResult(
                            title=result.get("title", ""),
                            link=result.get("link", ""),
                            snippet=result.get("snippet", ""),
                            source=result.get("displayed_link", result.get("link", "")),
                        )
                    )

            return search_results

        except Exception as e:
            raise Exception(f"SerpAPI search failed: {str(e)}")

    def search_news(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """Search for news articles.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of SearchResult objects from news sources
        """
        try:
            search = GoogleSearch(
                {
                    "q": query,
                    "api_key": self.api_key,
                    "tbm": "nws",  # News search
                    "num": min(num_results, 10),
                    "gl": "us",
                    "hl": "en",
                }
            )

            results = search.get_dict()
            search_results = []

            # Parse news results
            if "news_results" in results:
                for result in results["news_results"]:
                    search_results.append(
                        SearchResult(
                            title=result.get("title", ""),
                            link=result.get("link", ""),
                            snippet=result.get("snippet", ""),
                            source=result.get("source", ""),
                        )
                    )

            return search_results

        except Exception as e:
            raise Exception(f"SerpAPI news search failed: {str(e)}")

    def search_multiple_queries(
        self, queries: List[str], results_per_query: int = 5
    ) -> Dict[str, List[SearchResult]]:
        """Perform multiple searches for different queries.

        Args:
            queries: List of search queries
            results_per_query: Number of results per query

        Returns:
            Dictionary mapping queries to their search results
        """
        all_results = {}

        for query in queries:
            try:
                results = self.search(query, results_per_query)
                all_results[query] = results
            except Exception as e:
                print(f"Warning: Failed to search for '{query}': {str(e)}")
                all_results[query] = []

        return all_results
