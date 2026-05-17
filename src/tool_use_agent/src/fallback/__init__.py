"""
Fallback handling module
"""
from .handler import FallbackHandler, FallbackChain
from .strategies import (
    RetryHandler,
    AlternativeToolHandler,
    FallbackResponseHandler,
    GracefulDegradationHandler
)

__all__ = [
    "FallbackHandler",
    "FallbackChain",
    "RetryHandler",
    "AlternativeToolHandler",
    "FallbackResponseHandler",
    "GracefulDegradationHandler"
]