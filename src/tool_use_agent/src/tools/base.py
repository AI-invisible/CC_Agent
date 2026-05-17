"""
Base tool classes and interfaces
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ToolParameter:
    """Tool parameter definition"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    constraints: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required": self.required,
            "default": self.default,
            "constraints": self.constraints
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolParameter':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class ToolResult:
    """Tool execution result"""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_name: Optional[str] = None
    execution_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "tool_name": self.tool_name,
            "execution_time": self.execution_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolResult':
        """Create from dictionary"""
        return cls(**data)

    def to_formatted_string(self) -> str:
        """Format result as string for LLM"""
        if self.success:
            result_str = f"Tool '{self.tool_name}' executed successfully.\n"
            if isinstance(self.data, dict):
                result_str += json.dumps(self.data, indent=2, ensure_ascii=False)
            else:
                result_str += str(self.data)
            if self.execution_time:
                result_str += f"\nExecution time: {self.execution_time:.2f}s"
        else:
            result_str = f"Tool '{self.tool_name}' execution failed.\n"
            if self.error:
                result_str += f"Error: {self.error}"
        return result_str


class BaseTool(ABC):
    """Base tool class"""

    def __init__(self):
        """Initialize tool"""
        self._parameters: Dict[str, ToolParameter] = {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        pass

    @property
    def parameters(self) -> Dict[str, ToolParameter]:
        """Tool parameters definition"""
        return self._parameters

    @parameters.setter
    def parameters(self, value: Dict[str, ToolParameter]):
        """Set tool parameters"""
        self._parameters = value

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute tool

        Args:
            **kwargs: Tool parameters

        Returns:
            ToolResult: Execution result
        """
        pass

    def validate_parameters(self, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate parameters

        Args:
            params: Parameters to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required parameters
        for param_name, param_def in self.parameters.items():
            if param_def.required and param_name not in params:
                return False, f"Missing required parameter: {param_name}"

            # Validate parameter type
            if param_name in params:
                value = params[param_name]
                expected_type = param_def.type

                type_mapping = {
                    "string": str,
                    "integer": int,
                    "float": float,
                    "boolean": bool,
                    "array": list,
                    "object": dict
                }

                expected_python_type = type_mapping.get(expected_type)
                if expected_python_type and not isinstance(value, expected_python_type):
                    return False, f"Parameter '{param_name}' should be {expected_type}, got {type(value).__name__}"

                # Validate constraints
                if param_def.constraints:
                    if "min" in param_def.constraints and value < param_def.constraints["min"]:
                        return False, f"Parameter '{param_name}' should be >= {param_def.constraints['min']}"
                    if "max" in param_def.constraints and value > param_def.constraints["max"]:
                        return False, f"Parameter '{param_name}' should be <= {param_def.constraints['max']}"
                    if "min_length" in param_def.constraints and len(value) < param_def.constraints["min_length"]:
                        return False, f"Parameter '{param_name}' length should be >= {param_def.constraints['min_length']}"
                    if "max_length" in param_def.constraints and len(value) > param_def.constraints["max_length"]:
                        return False, f"Parameter '{param_name}' length should be <= {param_def.constraints['max_length']}"

        return True, None

    def get_function_schema(self) -> Dict[str, Any]:
        """
        Get tool function schema for LangChain/LangGraph

        Returns:
            Dict[str, Any]: Function schema
        """
        properties = {}
        required = []

        for param_name, param_def in self.parameters.items():
            properties[param_name] = {
                "type": param_def.type,
                "description": param_def.description
            }
            if param_def.default is not None:
                properties[param_name]["default"] = param_def.default

            if param_def.required:
                required.append(param_name)

            if param_def.constraints:
                properties[param_name].update(param_def.constraints)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

    async def __call__(self, **kwargs) -> ToolResult:
        """
        Call tool with validation

        Args:
            **kwargs: Tool parameters

        Returns:
            ToolResult: Execution result
        """
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(kwargs)
        if not is_valid:
            return ToolResult(
                success=False,
                data=None,
                error=f"Parameter validation failed: {error_msg}",
                tool_name=self.name
            )

        # Execute tool
        import time
        start_time = time.time()
        try:
            result = await self.execute(**kwargs)
            result.tool_name = self.name
            result.execution_time = time.time() - start_time
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                tool_name=self.name,
                execution_time=time.time() - start_time
            )