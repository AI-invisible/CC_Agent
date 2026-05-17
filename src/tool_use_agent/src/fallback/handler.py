"""
Fallback handling base classes
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio


class FallbackHandler(ABC):
    """Base class for fallback handlers"""

    @abstractmethod
    def can_handle(self, error: Exception) -> bool:
        """
        Check if this handler can handle the error

        Args:
            error: Exception to handle

        Returns:
            bool: True if handler can handle this error
        """
        pass

    @abstractmethod
    async def handle(self, error: Exception, context: Dict[str, Any]) -> str:
        """
        Handle the error and return fallback response

        Args:
            error: Exception to handle
            context: Execution context

        Returns:
            str: Fallback response message
        """
        pass

    def get_priority(self) -> int:
        """
        Get handler priority (higher = handled first)

        Returns:
            int: Handler priority
        """
        return 0


class FallbackChain:
    """Chain of fallback handlers"""

    def __init__(self):
        """Initialize fallback chain"""
        self._handlers: List[FallbackHandler] = []

    def add_handler(self, handler: FallbackHandler) -> None:
        """
        Add handler to chain

        Args:
            handler: Handler to add
        """
        self._handlers.append(handler)
        # Sort by priority (highest first)
        self._handlers.sort(key=lambda h: h.get_priority(), reverse=True)

    def remove_handler(self, handler: FallbackHandler) -> bool:
        """
        Remove handler from chain

        Args:
            handler: Handler to remove

        Returns:
            bool: True if handler was removed
        """
        if handler in self._handlers:
            self._handlers.remove(handler)
            return True
        return False

    def clear_handlers(self) -> None:
        """Clear all handlers"""
        self._handlers.clear()

    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> str:
        """
        Try to handle error with available handlers

        Args:
            error: Exception to handle
            context: Execution context

        Returns:
            str: Fallback response or error message
        """
        for handler in self._handlers:
            if handler.can_handle(error):
                try:
                    return await handler.handle(error, context)
                except Exception as e:
                    # Handler failed, try next one
                    continue

        # No handler could handle the error
        return f"An error occurred: {str(error)}"

    async def handle_with_timeout(
        self,
        error: Exception,
        context: Dict[str, Any],
        timeout: float = 10.0
    ) -> str:
        """
        Handle error with timeout

        Args:
            error: Exception to handle
            context: Execution context
            timeout: Timeout in seconds

        Returns:
            str: Fallback response or error message
        """
        try:
            return await asyncio.wait_for(
                self.handle_error(error, context),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return "Fallback handling timed out. Please try again."

    def get_handlers(self) -> List[FallbackHandler]:
        """Get all handlers in the chain"""
        return self._handlers.copy()

    def __len__(self) -> int:
        """Get number of handlers"""
        return len(self._handlers)

    def __contains__(self, handler: FallbackHandler) -> bool:
        """Check if handler is in chain"""
        return handler in self._handlers