"""Defines exception classes, error handling utilities, and a decorator for consistent and user-friendly error reporting in OARC Crawlers."""

import sys
import functools
import traceback
from typing import Any, Dict, Callable

import click

from oarc_utils.errors import OARCError


def get_error(error: Exception, verbose: bool = False) -> Dict[str, Any]:
    """Gets an error from an exception by returning a structured response.
    
    Args:
        error: The exception to handle
        verbose: Whether to include debug information in the output
        
    Returns:
        A dictionary containing error information
    """
    # Get error details
    error_type = type(error).__name__
    error_message = str(error)
    exit_code = getattr(error, 'exit_code', 1) if isinstance(error, OARCError) else 1
    
    # Only log in verbose mode - the report method will handle user output
    if verbose:
        click.secho(f"ERROR: {error_type}: {error_message}", fg="red")
        click.secho(traceback.format_exc(), fg="red")
        
    # Return structured error information
    result = {
        "success": False,
        "error": error_message,
        "error_type": error_type,
        "exit_code": exit_code
    }
    
    if verbose:
        result["traceback"] = traceback.format_exc()
        
    return result


def handle_error(func: Callable) -> Callable:
    """Decorator to wrap a Click command and handle exceptions.
    
    This decorator will catch any exceptions raised by the command,
    handle them appropriately, and exit with a suitable exit code using sys.exit().
    
    Args:
        func: The function to decorate
        
    Returns:
        A wrapped function that handles errors and exits.
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        verbose = kwargs.get('verbose', False)
        try:
            # Execute the original function. If it returns a value,
            # we might want to handle it or assume Click commands often don't
            # return meaningful values on success (or return 0).
            return func(*args, **kwargs) 
        except click.exceptions.UsageError as e:
            # Handle command not found errors cleanly
            if "No such command" in str(e):
                command_name = str(e).split("'")[1] if "'" in str(e) else "unknown"
                click.echo(f"Error: Command '{command_name}' not found", err=True)
                sys.exit(2)  # Use sys.exit
            else:
                # For other usage errors, still show them but without traceback
                click.echo(f"Error: {str(e)}", err=True)
                sys.exit(2)  # Use sys.exit
        except Exception as e:
            # report_error now returns the exit code, which we pass to sys.exit
            exit_code = report_error(e, verbose) 
            sys.exit(exit_code)  # Use sys.exit
    return wrapped


def report_error(error: Exception, verbose: bool = False) -> int:
    """Handle an exception, display it to the user, and return an exit code.
    
    Args:
        error: The exception to handle
        verbose: Whether to include debug information in the output
        
    Returns:
        An exit code suitable for sys.exit()
    """
    result = get_error(error, verbose)
    
    # Create a visually distinct error message for users
    if isinstance(error, OARCError):
        # For expected errors, display a concise message
        click.secho("╔═══════════════════════════════╗", fg="red")
        click.secho("║           ERROR               ║", fg="red", bold=True)
        click.secho("╚═══════════════════════════════╝", fg="red")
        click.secho(f"➤ {result['error']}", fg="red")
    else:
        # For unexpected errors, provide more context
        click.secho("╔═══════════════════════════════╗", fg="red")
        click.secho("║      UNEXPECTED ERROR         ║", fg="red", bold=True)
        click.secho("╚═══════════════════════════════╝", fg="red")
        click.secho(f"➤ {result['error_type']}: {result['error']}", fg="red")
        click.secho("Please report this error to the project maintainers.", fg="yellow")
    
    # Show traceback in verbose mode
    if verbose and "traceback" in result:
        click.echo()
        click.secho("Debug Information:", fg="blue", bold=True)
        click.echo(result["traceback"])
        
    return result["exit_code"]
