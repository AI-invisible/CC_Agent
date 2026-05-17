"""
Fallback handling strategies
"""
from typing import Dict, Any, Optional
import asyncio
from .handler import FallbackHandler


class RetryHandler(FallbackHandler):
    """Handler that retries failed operations"""

    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        """
        Initialize retry handler

        Args:
            max_retries: Maximum number of retries
            delay: Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.delay = delay

    def can_handle(self, error: Exception) -> bool:
        """Check if error is retryable"""
        # Retry on network errors, timeouts, etc.
        retryable_errors = (
            ConnectionError,
            TimeoutError,
            OSError,
        )
        return isinstance(error, retryable_errors)

    async def handle(self, error: Exception, context: Dict[str, Any]) -> str:
        """Handle error by retrying"""
        retry_func = context.get("retry_func")
        if not retry_func:
            raise ValueError("No retry function provided in context")

        retry_count = context.get("retry_count", 0)
        if retry_count >= self.max_retries:
            return f"Operation failed after {self.max_retries} retries: {str(error)}"

        # Wait before retry
        await asyncio.sleep(self.delay)

        # Update context for retry
        context["retry_count"] = retry_count + 1

        # Attempt retry
        try:
            result = await retry_func()
            if result:
                return f"Operation succeeded after {retry_count + 1} retries."
            else:
                raise Exception("Retry returned falsy result")
        except Exception as e:
            # Try next handler
            raise

    def get_priority(self) -> int:
        """High priority for retry handler"""
        return 100


class AlternativeToolHandler(FallbackHandler):
    """Handler that tries alternative tools"""

    def __init__(self):
        """Initialize alternative tool handler"""
        pass

    def can_handle(self, error: Exception) -> bool:
        """Check if error is tool-specific"""
        # Handle tool execution errors
        error_str = str(error).lower()
        return "tool" in error_str or "execution" in error_str

    async def handle(self, error: Exception, context: Dict[str, Any]) -> str:
        """Handle error by trying alternative tools"""
        tool_registry = context.get("tool_registry")
        failed_tool_name = context.get("tool_name")
        tool_params = context.get("tool_params", {})

        if not tool_registry or not failed_tool_name:
            return f"Tool execution failed: {str(error)}"

        # Find alternative tools
        alternatives = tool_registry.search(failed_tool_name.split("_")[0])

        # Try each alternative
        for alt_tool_name in alternatives:
            if alt_tool_name == failed_tool_name:
                continue

            try:
                result = await tool_registry.execute_tool(alt_tool_name, **tool_params)
                if result.success:
                    return f"Successfully used alternative tool '{alt_tool_name}'.\n{result.to_formatted_string()}"
            except Exception:
                continue

        return f"Primary tool '{failed_tool_name}' failed and no alternatives available: {str(error)}"

    def get_priority(self) -> int:
        """Medium priority for alternative tool handler"""
        return 50


class FallbackResponseHandler(FallbackHandler):
    """Handler that provides fallback responses"""

    def __init__(self, fallback_messages: Optional[Dict[str, str]] = None):
        """
        Initialize fallback response handler

        Args:
            fallback_messages: Mapping of error types to fallback messages
        """
        self.fallback_messages = fallback_messages or {
            "default": "I apologize, but I encountered an error. Please try again or rephrase your request.",
            "timeout": "The operation timed out. Please try again.",
            "network": "I'm having trouble connecting to external services. Please check your network connection.",
            "tool": "I encountered an error while using tools. Let me try a different approach.",
            "api": "There was an issue with the API. Please try again later."
        }

    def can_handle(self, error: Exception) -> bool:
        """This handler can handle any error"""
        return True

    async def handle(self, error: Exception, context: Dict[str, Any]) -> str:
        """Provide fallback response"""
        error_str = str(error).lower()

        # Determine error type
        error_type = "default"
        for key in self.fallback_messages:
            if key != "default" and key in error_str:
                error_type = key
                break

        # Get fallback message
        fallback_msg = self.fallback_messages.get(error_type, self.fallback_messages["default"])

        # Add error details if available
        if context.get("include_error_details", False):
            fallback_msg += f"\n\nError details: {str(error)}"

        return fallback_msg

    def get_priority(self) -> int:
        """Low priority for fallback response handler"""
        return 10


class GracefulDegradationHandler(FallbackHandler):
    """Handler that gracefully degrades functionality"""

    def __init__(self):
        """Initialize graceful degradation handler"""
        pass

    def can_handle(self, error: Exception) -> bool:
        """Check if error allows graceful degradation"""
        # Handle errors where we can provide partial functionality
        error_str = str(error).lower()
        return any(keyword in error_str for keyword in ["partial", "degraded", "limited"])

    async def handle(self, error: Exception, context: Dict[str, Any]) -> str:
        """Handle error with degraded functionality"""
        user_query = context.get("user_query", "")
        partial_results = context.get("partial_results")

        response = "I encountered an issue, but let me help you with what I can provide.\n\n"

        if partial_results:
            response += f"Here's what I was able to gather:\n{partial_results}\n\n"

        response += f"Regarding your question about '{user_query}', "
        response += "I can provide general guidance, but some specific details may not be available at the moment. "
        response += "Please try again later for complete information."

        return response

    def get_priority(self) -> int:
        """Medium priority for graceful degradation handler"""
        return 40