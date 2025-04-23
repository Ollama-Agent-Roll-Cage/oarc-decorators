[![Python package](https://github.com/Ollama-Agent-Roll-Cage/oarc-utils/actions/workflows/python-package.yml/badge.svg)](https://github.com/Ollama-Agent-Roll-Cage/oarc-utils/actions/workflows/python-package.yml)

# OARC-Utils

A global repository of useful Python decorators and custom error classes for the Ollama Agent Roll Cage (OARC) ecosystem. This package provides reusable components to streamline development across various OARC projects.

## Features

| Feature             | Description                                                                 |
| :------------------ | :-------------------------------------------------------------------------- |
| 🦄 **`@singleton`**    | Ensures only one instance of a class exists, with parameter checking.       |
| ⚡ **`@asyncio_run`**  | Runs an async function synchronously, useful for CLI tools (like Click).    |
| 🛡️ **`@handle_error`** | Wraps functions (especially Click commands) for consistent error handling.  |
| 🏭 **`@factory`**      | Adds a flexible `create` class method for object instantiation.             |
| 🚨 **Custom Errors**   | Provides a set of standardized `OarcError` subclasses for common issues.    |

## Setup

`oarc-decorators` requires Python >=3.10 and <3.12.

### Installation

```bash
# Install using pip
pip install oarc-decorators

# Or install using UV
uv pip install oarc-decorators
```

## Usage

Import decorators and error classes directly from the package:

```python
from oarc_decorators import (
    singleton,
    asyncio_run,
    handle_error,
    factory,
    NetworkError, 
    ConfigurationError,
    # ... other errors ...
)
import asyncio
import click
```

### Singleton Decorator (`@singleton`)

Ensures that only one instance of a class is created. It warns if subsequent instantiations attempt to use different parameters.

```python
# --- Singleton Example ---
@singleton
class SettingsManager:
    def __init__(self, config_path="settings.json"):
        print(f"Initializing SettingsManager with {config_path}")
        self.config_path = config_path
        # Load settings...

settings1 = SettingsManager()
settings2 = SettingsManager(config_path="other_settings.json") # Will warn about different params
assert settings1 is settings2

# Explicitly get the instance
instance = SettingsManager.get_instance() 
assert instance is settings1

# Reset for testing (if needed)
SettingsManager._reset_singleton() 
```

### Asyncio Run Decorator (`@asyncio_run`)

Allows an `async` function to be called from synchronous code by running it in the asyncio event loop. Particularly useful for integrating async logic into synchronous frameworks like Click.

```python
# --- Asyncio Run Example ---
@asyncio_run
async def perform_async_task():
    print("Starting async task...")
    await asyncio.sleep(1)
    print("Async task finished.")

# Call the async function synchronously
perform_async_task() 
```

### Error Handling Decorator (`@handle_error`)

Wraps a function (commonly a Click command) to provide consistent error handling. It catches specified exceptions, reports them using `click.secho` for user-friendly output, and returns an appropriate exit code.

```python
# --- Handle Error Example (with Click) ---
@click.command()
@click.option('--config', default='config.yaml', help='Path to config file.')
@click.option('--verbose', is_flag=True, help='Enable verbose output.')
@handle_error # Automatically handles errors and reports them via Click
def process_data(config, verbose):
    """Processes data based on the configuration."""
    click.echo(f"Processing data using {config}")
    if config == "error.yaml":
        raise ConfigurationError("Invalid configuration file specified.")
    elif config == "network_error.yaml":
        raise NetworkError("Failed to connect to the data source.")
    elif config == "unexpected.yaml":
        # Simulate an unexpected error
        result = 1 / 0 
    # Simulate success
    click.echo("Data processed successfully.")

# Example command-line execution (if saved as cli.py):
# python cli.py --config=valid.yaml
# python cli.py --config=error.yaml
# python cli.py --config=network_error.yaml
# python cli.py --config=unexpected.yaml --verbose 
```

### Factory Decorator (`@factory`)

Adds a `create(*args, **kwargs)` class method to the decorated class, providing a standardized way to instantiate objects. It includes special handling for passing arguments (e.g., from CLI parsing) and retrieving results stored in `_result`.

```python
# --- Factory Example ---
@factory
class Widget:
    def __init__(self, name, size):
        print(f"Creating widget '{name}' of size {size}")
        self.name = name
        self.size = size
        self._result = None # Optional: for factory to return if set

# Standard instantiation via factory method
widget1 = Widget.create(name="Sprocket", size=10)
widget2 = Widget.create(name="Cog", size=5)

# Example with special 'args' handling (if Widget.__init__ supported it)
# widget3 = Widget.create(args=['--name', 'Gadget', '--size', '15']) 
```

### Custom Error Classes

The package provides a hierarchy of custom exception classes inheriting from `OarcError` (which itself inherits from `Exception`). These allow for more specific error handling and reporting, especially when used with the `@handle_error` decorator.

```python
# --- Custom Error Example ---
def check_network_status(url):
    status = simulate_network_check(url) # Your function here
    if status == "offline":
        raise NetworkError(f"Unable to reach {url}. Please check your connection.")
    elif status == "unauthorized":
        raise AuthenticationError("Authentication failed for accessing resource.")
    return "Online"

try:
    check_network_status("http://example.com")
except NetworkError as ne:
    print(f"Network Issue: {ne}")
except AuthenticationError as ae:
    print(f"Auth Issue: {ae}")
except OarcError as oe: # Catch any other OARC-specific error
    print(f"OARC Error: {oe}")
except Exception as e: # Catch any other unexpected error
    print(f"Unexpected Error: {e}")

```

## API Reference

### Decorators

-   **`@singleton(cls)`**: Makes `cls` a singleton.
-   **`@asyncio_run(func)`**: Wraps async `func` to run synchronously.
-   **`@handle_error`**: Decorator (primarily for Click commands) to catch and report errors gracefully.
-   **`@factory(cls)`**: Adds a `create(*args, **kwargs)` class method to `cls`.

### Error Classes

Inherit from `OarcError` (which inherits from `Exception`).

-   `OarcError`
-   `AuthenticationError`
-   `BuildError`
-   `ConfigurationError`
-   `CrawlerOpError`
-   `DataExtractionError`
-   `NetworkError`
-   `PublishError`
-   `ResourceNotFoundError`
-   `MCPError` (Base error for MCP operations, inherits directly from `Exception`)
-   `TransportError` (Inherits from `MCPError`)

## Development

For development, clone the repository and install with development dependencies using UV:

```bash
# Clone the repository (replace with your fork/clone URL)
git clone https://github.com/Ollama-Agent-Roll-Cage/oarc-decorators.git
cd oarc-decorators

# Install UV package manager if you haven't already
pip install uv

# Create & activate virtual environment with UV (using Python 3.10 or 3.11)
uv venv --python 3.11
# On Windows: .venv\Scripts\activate
# On Unix/macOS: source .venv/bin/activate

# Install in editable mode with development dependencies
uv pip install -e ".[dev]"
```

### Running Tests

Tests are written using `pytest`. Ensure you have installed the development dependencies (`.[dev]`).

To run the test suite:

```bash
# Ensure your virtual environment is activated
uv run pytest
```

To run tests with coverage:

```bash
uv run pytest --cov=src/oarc_decorators --cov-report=term-missing
```

## Project Structure

```
oarc-decorators/
├── .flake8              # Flake8 configuration
├── .git/                # Git directory
├── .gitignore           # Git ignore rules
├── .pylintrc            # Pylint configuration
├── .venv/               # Virtual environment (if created locally)
├── docs/                # Documentation files
│   └── Specification.md # Detailed specifications
├── LICENSE              # Apache 2.0 License file
├── pyproject.toml       # Project metadata and dependencies (PEP 621)
├── pytest.ini           # Pytest configuration
├── README.md            # This file
├── src/                 # Source code directory
│   └── oarc_decorators/ # Main package directory
│       ├── __init__.py      # Exports decorators and errors
│       ├── asyncio_run.py   # @asyncio_run implementation
│       ├── factory.py       # @factory implementation
│       ├── handle_error.py  # @handle_error and error classes
│       └── singleton.py     # @singleton implementation
└── uv.lock              # UV lock file for reproducible dependencies
```

## License

This project is licensed under the [Apache 2.0 License](LICENSE)

## Citations

Please use the following BibTeX entry to cite this project:

```bibtex
@software{oarc,
  author = {Leo Borcherding, Kara Rawson},
  title = {OARC: Ollama Agent Roll Cage is a powerful multimodal toolkit for AI interactions, automation, and workflows.},
  date = {4-20-2026},
  howpublished = {\url{https://github.com/Ollama-Agent-Roll-Cage/oarc}}
}
```

## Contact

For questions or support, please contact us at:

- **Email**: <NotSetup@gmail.com>
- **Issues**: [GitHub Issues](https://github.com/Ollama-Agent-Roll-Cage/oarc-decorators/issues)
