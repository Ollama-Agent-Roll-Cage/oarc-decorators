"""
oarc_utils.errors

This module defines custom exception classes for the OARC Crawler project.
All error classes inherit from the base `OarcError`, providing a unified interface for error handling
across the project. These exceptions cover authentication, configuration, network, data extraction,
and other crawler-related error scenarios.
"""

from .oarc_crawlers_errors import (
    OARCError,
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

__all__ = [
    "OARCError",
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
