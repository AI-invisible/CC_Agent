"""
Function tool wrapper for converting functions to tools
"""
from typing import Callable, Dict, Any, Optional
import inspect
from .base import BaseTool, ToolResult, ToolParameter


class FunctionTool(BaseTool):
    """Tool wrapper for callable functions"""

    def __init__(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Dict[str, Any]]] = None
    ):
        """
        Initialize function tool

        Args:
            func: Function to wrap
            name: Tool name (defaults to function name)
            description: Tool description
            parameters: Parameter definitions
        """
        super().__init__()
        self._func = func
        self._name = name or func.__name__
        self._description = description or func.__doc__ or f"Tool: {self._name}"

        # Parse parameters from function signature if not provided
        if parameters:
            self._parse_parameters_from_definition(parameters)
        else:
            self._parse_parameters_from_signature()

    @property
    def name(self) -> str:
        """Tool name"""
        return self._name

    @property
    def description(self) -> str:
        """Tool description"""
        return self._description

    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the wrapped function

        Args:
            **kwargs: Function parameters

        Returns:
            ToolResult: Execution result
        """
        try:
            # Check if function is async
            if inspect.iscoroutinefunction(self._func):
                result = await self._func(**kwargs)
            else:
                result = self._func(**kwargs)

            return ToolResult(
                success=True,
                data=result,
                tool_name=self.name
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                tool_name=self.name
            )

    def _parse_parameters_from_definition(self, parameters: Dict[str, Dict[str, Any]]) -> None:
        """
        Parse parameters from explicit definition

        Args:
            parameters: Parameter definitions
        """
        param_objects = {}
        for param_name, param_def in parameters.items():
            param_objects[param_name] = ToolParameter(
                name=param_name,
                type=param_def.get("type", "string"),
                description=param_def.get("description", ""),
                required=param_def.get("required", True),
                default=param_def.get("default"),
                constraints=param_def.get("constraints")
            )
        self.parameters = param_objects

    def _parse_parameters_from_signature(self) -> None:
        """Parse parameters from function signature"""
        sig = inspect.signature(self._func)
        param_objects = {}

        for param_name, param in sig.parameters.items():
            # Skip 'self' parameter
            if param_name == 'self':
                continue

            # Determine parameter type
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                type_mapping = {
                    str: "string",
                    int: "integer",
                    float: "float",
                    bool: "boolean",
                    list: "array",
                    dict: "object"
                }
                param_type = type_mapping.get(param.annotation, "string")

            # Determine if required
            required = param.default == inspect.Parameter.empty

            # Create parameter object
            param_objects[param_name] = ToolParameter(
                name=param_name,
                type=param_type,
                description=f"Parameter: {param_name}",
                required=required,
                default=param.default if param.default != inspect.Parameter.empty else None
            )

        self.parameters = param_objects


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    parameters: Optional[Dict[str, Dict[str, Any]]] = None
):
    """
    Decorator to convert a function to a tool

    Args:
        name: Tool name
        description: Tool description
        parameters: Parameter definitions

    Returns:
        Callable: Decorator function
    """
    def decorator(func: Callable) -> FunctionTool:
        return FunctionTool(func, name=name, description=description, parameters=parameters)
    return decorator