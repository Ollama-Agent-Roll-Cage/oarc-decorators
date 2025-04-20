"""
oarc_utils.decorators

This module exposes global decorators for use throughout the OARC project.
Decorators include error handling, singleton pattern, async helpers, and factory utilities.
"""

from .asyncio_run import asyncio_run
from .factory import factory
from .handle_error import handle_error, get_error, report_error
from .singleton import singleton

__all__ = [
    # Decorators
    "singleton",
    "asyncio_run",
    "handle_error",
    "factory",
    # Error Functions
    "get_error",
    "report_error",]
