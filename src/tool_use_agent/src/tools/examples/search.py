"""
Search tool example (simulated)
"""
from typing import Dict, Any, List
import random
from ..base import BaseTool, ToolResult, ToolParameter


class SearchTool(BaseTool):
    """Simulated search tool"""

    def __init__(self):
        """Initialize search tool"""
        super().__init__()
        self._parameters = {
            "query": ToolParameter(
                name="query",
                type="string",
                description="Search query",
                required=True
            ),
            "num_results": ToolParameter(
                name="num_results",
                type="integer",
                description="Number of results to return",
                required=False,
                default=5
            )
        }

    @property
    def name(self) -> str:
        """Tool name"""
        return "search"

    @property
    def description(self) -> str:
        """Tool description"""
        return "Search for information on the web"

    async def execute(self, query: str, num_results: int = 5) -> ToolResult:
        """
        Perform search (simulated)

        Args:
            query: Search query
            num_results: Number of results

        Returns:
            ToolResult: Search results
        """
        # Simulate search results
        results = []
        for i in range(min(num_results, 10)):
            results.append({
                "title": f"Search result {i+1} for '{query}'",
                "url": f"https://example.com/result/{i+1}",
                "snippet": f"This is a simulated search result for query: {query}. "
                          f"Result {i+1} contains relevant information."
            })

        return ToolResult(
            success=True,
            data={
                "query": query,
                "total_results": random.randint(100, 10000),
                "results": results
            },
            metadata={"source": "simulated"}
        )