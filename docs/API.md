# OARC Decorators API Reference

This document provides a detailed API reference for the decorators and error classes available in the `oarc-decorators` package.

## Decorators

---

### `@singleton`

**Signature:** `singleton(cls: Type[T]) -> Type[T]`

**Purpose:**
Transforms a class into a Singleton, ensuring that only one instance of the class is ever created during the application's lifecycle. It intercepts class instantiation (`__new__`) and initialization (`__init__`).

**Behavior:**
1.  **First Instantiation:** When the decorated class is instantiated for the first time (e.g., `MyClass()`), the original `__new__` and `__init__` are called, and the resulting instance is stored internally. The arguments passed to `__init__` are also stored.
2.  **Subsequent Instantiations:** Any subsequent attempt to instantiate the class (e.g., `MyClass()`, `MyClass(arg='new')`) will return the *originally created instance*.
3.  **Parameter Mismatch Warning:** If subsequent instantiations provide different arguments to `__init__` compared to the first instantiation, a warning message detailing the differences is printed to the console using `click.secho` (yellow text). The original instance is still returned, and the new `__init__` call is effectively skipped.
4.  **Added Class Methods:**
    *   `get_instance()`: A class method to explicitly retrieve the singleton instance. If the instance hasn't been created yet, it calls the constructor with no arguments (`cls()`).
    *   `reset_singleton()`: A class method primarily for testing purposes. It removes the stored singleton instance, allowing the next instantiation to create a new one.

**Arguments:**
-   `cls` (`Type[T]`): The class to be decorated.

**Returns:**
-   `Type[T]`: The modified class with singleton behavior.

**Example:**
```python
from oarc_decorators import singleton
import click # Used internally for warnings

@singleton
class DatabaseConnector:
    def __init__(self, db_url: str = "default_url"):
        click.echo(f"Initializing DatabaseConnector with URL: {db_url}")
        self.db_url = db_url
        self.connection = f"Connected to {db_url}" # Simulate connection

# First instantiation
conn1 = DatabaseConnector("postgresql://user:pass@host:port/db") 
# Output: Initializing DatabaseConnector with URL: postgresql://user:pass@host:port/db

# Second instantiation with different args
conn2 = DatabaseConnector("mysql://user:pass@other_host:port/db") 
# Output (Warning via click.secho): 
# WARNING: Requested DatabaseConnector instance with different parameters: db_url=mysql://user:pass@other_host:port/db (was postgresql://user:pass@host:port/db). Using existing instance with original parameters.

# Third instantiation using get_instance
conn3 = DatabaseConnector.get_instance()

print(f"Conn1 URL: {conn1.db_url}") # Output: Conn1 URL: postgresql://user:pass@host:port/db
print(f"Conn2 URL: {conn2.db_url}") # Output: Conn2 URL: postgresql://user:pass@host:port/db
print(f"Conn3 URL: {conn3.db_url}") # Output: Conn3 URL: postgresql://user:pass@host:port/db
assert conn1 is conn2 is conn3

# Reset for testing
DatabaseConnector.reset_singleton()
conn4 = DatabaseConnector("new_default_url") # Now creates a new instance
# Output: Initializing DatabaseConnector with URL: new_default_url
print(f"Conn4 URL: {conn4.db_url}") # Output: Conn4 URL: new_default_url
```

---

### `@asyncio_run`

**Signature:** `asyncio_run(f: Callable[..., Coroutine]) -> Callable[..., Any]`

**Purpose:**
Provides a simple way to run an `async` function from synchronous code. It wraps the asynchronous function `f` in a synchronous `wrapper` function that calls `asyncio.run(f(*args, **kwargs))`.

**Behavior:**
-   When the decorated function is called, it blocks until the underlying `async` function completes its execution within a new asyncio event loop.
-   It's primarily intended for top-level script execution or integrating async functions into synchronous frameworks like Click commands.

**Arguments:**
-   `f` (`Callable[..., Coroutine]`): The asynchronous function (`async def`) to wrap.

**Returns:**
-   `Callable[..., Any]`: A synchronous wrapper function that executes the original async function and returns its result.

**Example:**
```python
from oarc_decorators import asyncio_run
import asyncio
import click

async def fetch_data(url: str) -> dict:
    print(f"Fetching data from {url}...")
    await asyncio.sleep(0.5) # Simulate network request
    print("Data fetched.")
    return {"url": url, "status": "success"}

@click.command()
@click.argument('url')
@asyncio_run # Make the async function callable by Click
def main(url: str):
    """Fetches data from a URL."""
    result = fetch_data(url) # Call the async function synchronously
    click.echo(f"Result: {result}")

# if __name__ == "__main__":
#     main() # Run via Click: python your_script.py http://example.com
```

---

### `@handle_error`

**Signature:** `handle_error(func: Callable) -> Callable`

**Purpose:**
A decorator designed to provide robust and user-friendly error handling, especially for Click commands. It wraps the function in a `try...except` block to catch and report errors consistently.

**Behavior:**
1.  **Execution:** Attempts to execute the wrapped function `func`.
2.  **Success:** If `func` completes without exceptions, its return value is returned.
3.  **`click.exceptions.UsageError` Handling:** Catches Click's `UsageError`.
    *   If the error message contains "No such command", it prints a specific "Command '...' not found" message.
    *   Otherwise, it prints a generic "Error: {error message}".
    *   Returns exit code `2`.
4.  **`OarcError` Handling:** Catches any exception inheriting from `OarcError` (defined within `handle_error.py`).
    *   Calls `report_error` to display a formatted error message using `click.secho` (Red box with "ERROR").
    *   If the `verbose` keyword argument passed to the decorated function is `True`, it also prints the traceback.
    *   Returns the `exit_code` attribute defined on the specific `OarcError` subclass (or 1 if not defined).
5.  **Other `Exception` Handling:** Catches any other standard Python `Exception`.
    *   Calls `report_error` to display a formatted error message (Red box with "UNEXPECTED ERROR").
    *   If `verbose` is `True`, it prints the traceback.
    *   Returns exit code `1`.
6.  **Verbose Argument:** The decorator expects the decorated function to potentially receive a `verbose` keyword argument (e.g., from `@click.option('--verbose', is_flag=True)`). It retrieves this argument using `kwargs.get('verbose', False)` to control traceback visibility.

**Arguments:**
-   `func` (`Callable`): The function (typically a Click command) to decorate.

**Returns:**
-   `Callable`: The wrapped function with error handling logic. The return value of the wrapped function will be the original function's return value on success, or an integer exit code on error.

**Example:**
```python
from oarc_decorators import handle_error, ConfigurationError, NetworkError
import click

@click.command()
@click.option('--mode', required=True, type=click.Choice(['fast', 'slow', 'fail_config', 'fail_network', 'fail_unexpected']))
@click.option('--verbose', is_flag=True, help='Show detailed error traceback.')
@handle_error # Apply the decorator
def run_process(mode, verbose):
    """Runs a process in different modes."""
    click.echo(f"Running in {mode} mode. Verbose: {verbose}")

    if mode == 'fail_config':
        raise ConfigurationError("Configuration file is corrupted.")
    elif mode == 'fail_network':
        raise NetworkError("Cannot reach the processing server.")
    elif mode == 'fail_unexpected':
        x = {}
        print(x['non_existent_key']) # Raises KeyError
    
    click.echo(f"Process completed successfully in {mode} mode.")
    return 0 # Explicit success exit code (optional)

# if __name__ == "__main__":
#     run_process() 
# Example CLI runs:
# python your_script.py --mode=fast
# python your_script.py --mode=fail_config
# python your_script.py --mode=fail_network --verbose
# python your_script.py --mode=fail_unexpected --verbose
# python your_script.py --mode=invalid_choice # Handled by Click UsageError
# python your_script.py --invalid-option # Handled by Click UsageError
```

---

### `@factory`

**Signature:** `factory(cls: Type[T]) -> Type[T]`

**Purpose:**
A class decorator that adds a standard `create` class method to the decorated class. This promotes the Factory pattern by providing a consistent entry point for object creation.

**Behavior:**
1.  **Adds `create` Method:** Injects a `@classmethod` named `create` into the decorated class `cls`.
2.  **`create` Method Logic:**
    *   Accepts arbitrary positional (`*args`) and keyword (`**kwargs`) arguments.
    *   **Special `args` Handling:** If `kwargs` contains the key `'args'` *and* no positional arguments (`*args`) were provided, it assumes `kwargs['args']` is a list or tuple intended for special processing (e.g., CLI arguments) and calls `cls(args=kwargs['args'])`.
    *   **Standard Instantiation:** Otherwise, it calls the class constructor normally using `cls(*args, **kwargs)`.
    *   **`_result` Attribute Check:** After instantiation, it checks if the created `instance` has an attribute named `_result` and if its value is not `None`. If both conditions are true, it returns `instance._result`. This allows classes that perform processing during `__init__` to return a specific result directly via the factory method.
    *   **Return Instance:** If `_result` is not found or is `None`, it returns the newly created `instance`.

**Arguments:**
-   `cls` (`Type[T]`): The class to be decorated.

**Returns:**
-   `Type[T]`: The modified class with the added `create` class method.

**Example:**
```python
from oarc_decorators import factory
from typing import List, Optional

@factory
class ReportGenerator:
    def __init__(self, data: dict, format: str = "json", args: Optional[List[str]] = None):
        self._result = None # Initialize optional result
        if args:
            # Example: Parse args if provided via create(args=...)
            print(f"Initializing with args: {args}")
            # ... parsing logic ...
            self.report_content = f"Report from args: {args}"
        else:
            print(f"Initializing with data: {data}, format: {format}")
            # ... standard init logic ...
            self.report_content = f"Report ({format}): {data}"
        
        # Optionally set _result if factory should return it directly
        self._result = self.generate_report() 

    def generate_report(self) -> str:
        # Simulate report generation
        return f"Generated: {self.report_content}"

# Standard creation
report1_result = ReportGenerator.create(data={"value": 1}, format="xml")
# Output: Initializing with data: {'value': 1}, format: xml
print(report1_result) 
# Output: Generated: Report (xml): {'value': 1} 

# Creation using special 'args' keyword
report2_result = ReportGenerator.create(args=["--source", "db", "--type", "summary"])
# Output: Initializing with args: ['--source', 'db', '--type', 'summary']
print(report2_result)
# Output: Generated: Report from args: ['--source', 'db', '--type', 'summary']

# If _result wasn't set, create would return the instance:
# report_instance = ReportGenerator.create(data={"value": 2}) 
# print(report_instance.report_content) 
```

---

## Error Classes

These classes provide standardized exceptions for common error conditions within the OARC ecosystem. They are designed to work well with the `@handle_error` decorator, which uses their `exit_code` attribute and type for reporting.

**Base Classes:**
-   `OarcError(Exception)`: Base for most OARC-specific operational errors.
    -   `exit_code`: `int` (Defaults to 1). Used by `@handle_error`.
-   `MCPError(Exception)`: Base for Multi-Control Plane (MCP) related errors. Does not define `exit_code`.

**Specific Error Classes:**

| Class                 | Inherits From | Default `exit_code` | Description                                      |
| :-------------------- | :------------ | :------------------ | :----------------------------------------------- |
| `AuthenticationError` | `OarcError`   | 4                   | Authentication failure.                          |
| `BuildError`          | `OarcError`   | 7                   | Error during package build operations.           |
| `ConfigurationError`  | `OarcError`   | 9                   | Problem with application configuration.          |
| `CrawlerOpError`      | `OarcError`   | 6                   | Generic failure during a crawler operation.      |
| `DataExtractionError` | `OarcError`   | 5                   | Failure during data extraction/parsing.          |
| `NetworkError`        | `OarcError`   | 2                   | Network operation failure (connection, timeout). |
| `PublishError`        | `OarcError`   | 8                   | Error during package publishing operations.      |
| `ResourceNotFoundError`| `OarcError`   | 3                   | A requested resource (file, URL) was not found.  |
| `TransportError`      | `MCPError`    | N/A                 | Error related to MCP transport layer.            |

**Usage:**
Raise these exceptions in your code where appropriate. If the function is decorated with `@handle_error`, the error will be caught, reported to the user via Click, and the program will exit with the corresponding `exit_code`.

```python
from oarc_decorators import handle_error, ResourceNotFoundError, ConfigurationError
import click
import os

CONFIG_PATH = "./app.conf"

@click.command()
@handle_error
def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise ResourceNotFoundError(f"Configuration file not found at: {CONFIG_PATH}")
    
    try:
        # Simulate loading config
        with open(CONFIG_PATH, 'r') as f:
            content = f.read()
            if "invalid_setting" in content:
                 raise ConfigurationError("Invalid setting found in configuration file.")
        click.echo("Configuration loaded successfully.")
    except IOError as e:
        # Example of wrapping a standard error
        raise OarcError(f"Failed to read configuration file: {e}", exit_code=10) # Custom exit code

# if __name__ == "__main__":
#     load_config()
```
