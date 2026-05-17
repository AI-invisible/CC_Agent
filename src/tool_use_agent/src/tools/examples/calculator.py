"""
Calculator tool example
"""
from typing import Dict, Any
from ..base import BaseTool, ToolResult, ToolParameter


class CalculatorTool(BaseTool):
    """Simple calculator tool"""

    def __init__(self):
        """Initialize calculator tool"""
        super().__init__()
        self._parameters = {
            "operation": ToolParameter(
                name="operation",
                type="string",
                description="Mathematical operation to perform: add, subtract, multiply, divide",
                required=True
            ),
            "a": ToolParameter(
                name="a",
                type="float",
                description="First operand",
                required=True
            ),
            "b": ToolParameter(
                name="b",
                type="float",
                description="Second operand",
                required=True
            )
        }

    @property
    def name(self) -> str:
        """Tool name"""
        return "calculator"

    @property
    def description(self) -> str:
        """Tool description"""
        return "Perform basic mathematical operations (add, subtract, multiply, divide)"

    async def execute(self, operation: str, a: float, b: float) -> ToolResult:
        """
        Execute calculator operation

        Args:
            operation: Operation to perform
            a: First operand
            b: Second operand

        Returns:
            ToolResult: Calculation result
        """
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else None
        }

        if operation not in operations:
            return ToolResult(
                success=False,
                data=None,
                error=f"Unknown operation: {operation}. Available: {', '.join(operations.keys())}"
            )

        if operation == "divide" and b == 0:
            return ToolResult(
                success=False,
                data=None,
                error="Division by zero is not allowed"
            )

        result = operations[operation](a, b)

        return ToolResult(
            success=True,
            data={
                "operation": operation,
                "operands": [a, b],
                "result": result
            }
        )