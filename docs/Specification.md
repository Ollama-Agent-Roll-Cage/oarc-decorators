# OARC Decorators Specification

This document outlines the specifications for the decorators and error classes provided in the `oarc-decorators` package.

## Decorators

### `@asyncio_run`

**Purpose:** Runs an async function synchronously by wrapping it and using `asyncio.run()`. Useful for integrating async functions into synchronous frameworks like Click CLI commands.

**Signature:** `asyncio_run(func: Callable[..., Coroutine]) -> Callable[..., Any]`

**Usage:**
```python
from oarc_decorators import asyncio_run
import asyncio
import click

@click.command()
@asyncio_run
async def my_async_command():
    """A Click command that runs an async task."""
    await asyncio.sleep(1)
    click.echo("Async task finished within Click command.")

# my_async_command() # Run via Click CLI
```

### `@handle_error`

**Purpose:** Wraps a function (typically a Click command) to provide standardized error handling. Catches `Exception` (by default), reports errors using `click.secho`, handles `click.exceptions.UsageError` specifically, and returns an appropriate exit code. Assumes a `verbose` keyword argument exists in the decorated function for controlling traceback visibility.

**Signature:** `handle_error(func: Callable) -> Callable`

**Usage:**
```python
from oarc_decorators import handle_error, ConfigurationError, NetworkError
import click

@click.command()
@click.option('--config', default='config.yaml')
@click.option('--verbose', is_flag=True)
@handle_error 
def process_data(config, verbose):
    """Processes data, handling errors."""
    click.echo(f"Processing with {config}, verbose={verbose}")
    if config == "error.yaml":
        raise ConfigurationError("Invalid config!")
    elif config == "network.yaml":
        raise NetworkError("Connection failed!")
    elif config == "unexpected.yaml":
        1 / 0 # Raise ZeroDivisionError
    click.echo("Success!")

# process_data() # Run via Click CLI
# Example runs:
# python your_script.py --config=good.yaml
# python your_script.py --config=error.yaml
# python your_script.py --config=network.yaml
# python your_script.py --config=unexpected.yaml --verbose
```

### `@singleton`

**Purpose:** Ensures that only one instance of a class is ever created using the Singleton pattern. It modifies the class's `__new__` and `__init__` methods. It warns via `click.secho` if subsequent instantiations attempt to use different `__init__` arguments. Adds `get_instance()` and `_reset_singleton()` class methods.

**Signature:** `singleton(cls: Type[T]) -> Type[T]`

**Usage:**
```python
from oarc_decorators import singleton

@singleton
class Settings:
    def __init__(self, setting_a="default_a"):
        print(f"Initializing Settings with setting_a={setting_a}")
        self.setting_a = setting_a

s1 = Settings() # Initializes
s2 = Settings(setting_a="new_value") # Warns, returns s1
s3 = Settings.get_instance() # Returns s1

assert s1 is s2 is s3
Settings._reset_singleton() # Clears instance for testing
s4 = Settings() # Re-initializes
```

### `@factory`

**Purpose:** Adds a `create(*args, **kwargs)` class method to the decorated class. This provides a standardized way to instantiate objects. It includes special handling for an `args` keyword argument (intended for CLI-style list of arguments) and can return the value of an instance's `_result` attribute if set after initialization.

**Signature:** `factory(cls: Type[T]) -> Type[T]`

**Usage:**
```python
from oarc_decorators import factory

@factory
class Processor:
    def __init__(self, data, mode="normal"):
        print(f"Initializing Processor with data: {data}, mode: {mode}")
        self.data = data
        self.mode = mode
        self._result = f"Processed {data}" # Optional result

p1 = Processor.create(data="input1")
p2 = Processor.create(data="input2", mode="fast")

# Access instance or result if _result was set
print(p1) # Prints the result: "Processed input1"
# print(p2.data) # Access instance attributes if needed (though factory returns _result here)

# Example with 'args' (if __init__ was designed to handle it)
# p3 = Processor.create(args=["--data", "input3", "--mode", "special"])
```

## Error Classes

Provides a hierarchy of custom exceptions for standardized error handling within the OARC ecosystem, primarily designed for use with `@handle_error`.

**Base Class:** `OarcError(Exception)` - Most custom errors inherit from this. It includes an `exit_code` attribute (defaulting to 1).
**Other Base:** `MCPError(Exception)` - Base for MCP-specific errors.

**Hierarchy:**
-   `OarcError`
    -   `AuthenticationError` (exit_code=4)
    -   `BuildError` (exit_code=7)
    -   `ConfigurationError` (exit_code=9)
    -   `CrawlerOpError` (exit_code=6)
    -   `DataExtractionError` (exit_code=5)
    -   `NetworkError` (exit_code=2)
    -   `PublishError` (exit_code=8)
    -   `ResourceNotFoundError` (exit_code=3)
    -   `MCPError`
    -   `TransportError`

**Usage:** Raise these errors within functions decorated by `@handle_error` for consistent reporting and exit codes.

```python
from oarc_decorators import handle_error, NetworkError
import click

@click.command()
@handle_error
def connect_to_service():
    if not check_connection():
        raise NetworkError("Service unreachable.")
    click.echo("Connected successfully.")

# connect_to_service() # Run via Click CLI
```
