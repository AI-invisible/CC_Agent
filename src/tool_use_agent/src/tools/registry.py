"""
Tool registry for managing available tools
"""
from typing import Dict, List, Optional, Callable, Any
from .base import BaseTool, ToolResult


class ToolRegistry:
    """Registry for managing available tools"""

    def __init__(self):
        """Initialize tool registry"""
        self._tools: Dict[str, BaseTool] = {}
        self._tool_aliases: Dict[str, str] = {}

    def register(self, tool: BaseTool, alias: Optional[str] = None) -> None:
        """
        Register a tool

        Args:
            tool: Tool instance to register
            alias: Optional alias for the tool
        """
        self._tools[tool.name] = tool
        if alias:
            self._tool_aliases[alias] = tool.name

    def register_decorator(self, func: Callable, **tool_kwargs) -> Callable:
        """
        Decorator to register a function as a tool

        Args:
            func: Function to register
            **tool_kwargs: Tool metadata (name, description, parameters)

        Returns:
            Callable: Wrapped function
        """
        from .function_tool import FunctionTool
        tool = FunctionTool(func=func, **tool_kwargs)
        self.register(tool)
        return func

    def get(self, name: str) -> Optional[BaseTool]:
        """
        Get tool by name or alias

        Args:
            name: Tool name or alias

        Returns:
            BaseTool: Tool instance or None if not found
        """
        # Check direct name
        if name in self._tools:
            return self._tools[name]

        # Check alias
        if name in self._tool_aliases:
            return self._tools[self._tool_aliases[name]]

        return None

    def get_all(self) -> Dict[str, BaseTool]:
        """
        Get all registered tools

        Returns:
            Dict[str, BaseTool]: All tools
        """
        return self._tools.copy()

    def list_tools(self) -> List[str]:
        """
        List all tool names

        Returns:
            List[str]: List of tool names
        """
        return list(self._tools.keys())

    def unregister(self, name: str) -> bool:
        """
        Unregister a tool

        Args:
            name: Tool name or alias

        Returns:
            bool: True if tool was removed, False if not found
        """
        # Check if it's an alias
        if name in self._tool_aliases:
            actual_name = self._tool_aliases[name]
            del self._tool_aliases[name]
            return self.unregister(actual_name)

        # Remove tool
        if name in self._tools:
            del self._tools[name]
            # Remove aliases pointing to this tool
            self._tool_aliases = {k: v for k, v in self._tool_aliases.items() if v != name}
            return True

        return False

    def search(self, query: str) -> List[str]:
        """
        Search tools by name or description

        Args:
            query: Search query

        Returns:
            List[str]: Matching tool names
        """
        query_lower = query.lower()
        results = []

        for name, tool in self._tools.items():
            if (query_lower in name.lower() or
                query_lower in tool.description.lower()):
                results.append(name)

        return results

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get function schemas for all tools (for LangChain/LangGraph)

        Returns:
            List[Dict[str, Any]]: List of function schemas
        """
        return [tool.get_function_schema() for tool in self._tools.values()]

    async def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """
        Execute a tool by name

        Args:
            name: Tool name
            **kwargs: Tool parameters

        Returns:
            ToolResult: Execution result
        """
        tool = self.get(name)
        if not tool:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool not found: {name}",
                tool_name=name
            )

        return await tool(**kwargs)

    def clear(self) -> None:
        """Clear all registered tools"""
        self._tools.clear()
        self._tool_aliases.clear()

    def __len__(self) -> int:
        """Get number of registered tools"""
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        """Check if tool is registered"""
        return name in self._tools or name in self._tool_aliases