"""
oarc_decorators

This module provides global decorators and error classes for use throughout the project.
"""

from .asyncio_run import asyncio_run
from .factory import factory
from .handle_error import (
    handle_error,
    OarcError,
    AuthenticationError,
    BuildError,
    ConfigurationError,
    CrawlerOpError,
    DataExtractionError,
    MCPError,
    NetworkError,
    PublishError,
    ResourceNotFoundError,
    TransportError,
)
from .singleton import singleton

__all__ = [
    # Decorators
    "singleton",
    "asyncio_run",
    "handle_error",
    "factory",
    # Error Classes
    "OarcError",
    "AuthenticationError",
    "BuildError",
    "ConfigurationError",
    "CrawlerOpError",
    "DataExtractionError",
    "MCPError",
    "NetworkError",
    "PublishError",
    "ResourceNotFoundError",
    "TransportError",
]
