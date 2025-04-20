"""Global decorators and error classes for the project"""
from .asyncio_run import asyncio_run
from .handle_error import (
    handle_error,
    # Import error classes
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
    TransportError
)
from .singleton import singleton
from .factory import factory

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
    "TransportError"
]