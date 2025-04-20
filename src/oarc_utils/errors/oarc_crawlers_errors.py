# Base exception classes
class OARCError(Exception):
    """Base exception for all OARC Crawler errors."""
    exit_code = 1


class AuthenticationError(OARCError):
    """Raised when authentication fails."""
    exit_code = 4


class BuildError(OARCError):
    """Raised during package build operations."""
    exit_code = 7


class ConfigurationError(OARCError):
    """Raised when there's a problem with configuration."""
    exit_code = 9


class CrawlerOpError(OARCError):
    """Raised when a crawler operation fails."""
    exit_code = 6


class DataExtractionError(OARCError):
    """Raised when data extraction fails."""
    exit_code = 5


class MCPError(Exception):
    """Base error for MCP operations."""
    pass


class NetworkError(OARCError):
    """Raised when network operations fail."""
    exit_code = 2


class PublishError(OARCError):
    """Raised during package publishing operations."""
    exit_code = 8


class ResourceNotFoundError(OARCError):
    """Raised when a requested resource is not found."""
    exit_code = 3


class TransportError(MCPError):
    """Error for transport-related issues."""
    pass
