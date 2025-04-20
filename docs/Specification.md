# OARC Decorators Specification

This document outlines the specifications for the decorators provided in the `oarc-decorators` package.

## Decorators

### `@asyncio_run`

**Purpose:** Runs an async function synchronously. Useful for top-level script execution or testing.

**Signature:** `asyncio_run(func)`

**Usage:**
```python
from oarc_decorators import asyncio_run
import asyncio

@asyncio_run
async def my_async_main():
    await asyncio.sleep(1)
    print("Async task finished.")

# Calling my_async_main() will block until the async function completes.
```

### `@handle_error`

**Purpose:** Provides a standard way to catch and log exceptions within a function. Can be configured for specific exception types and logging levels.

**Signature:** `handle_error(*, log_level="error", exceptions=(Exception,), message=None)`

**Usage:**
```python
from oarc_decorators import handle_error

@handle_error(log_level="warning", exceptions=(ValueError,), message="Caught a value error!")
def potentially_failing_function(value):
    if value < 0:
        raise ValueError("Value cannot be negative")
    print(f"Value is {value}")

potentially_failing_function(-1) # Will log a warning and the custom message
potentially_failing_function(10) # Will execute normally
```

### `@singleton`

**Purpose:** Ensures that only one instance of a class is ever created.

**Signature:** `singleton(cls)`

**Usage:**
```python
from oarc_decorators import singleton

@singleton
class DatabaseConnection:
    def __init__(self):
        print("Initializing DB Connection (should happen only once)")
        # Simulate connection setup
        self.connection = "established"

conn1 = DatabaseConnection()
conn2 = DatabaseConnection()

assert conn1 is conn2 # This assertion will pass
```

### `@factory`

**Purpose:** Implements the factory pattern, allowing a class to delegate object creation to subclasses or specific methods based on input parameters.

**Signature:** `factory(key_param, registry_attr="_registry")`

**Usage:** (Conceptual - implementation details may vary)
```python
from oarc_decorators import factory

class Shape:
    _registry = {} # Registry needs to be defined

    @classmethod
    @factory(key_param='shape_type')
    def create_shape(cls, shape_type, **kwargs):
        # The factory decorator handles looking up 'shape_type' in _registry
        # and calling the appropriate subclass's __init__ or a registered method.
        # If not found, it might raise an error or return None.
        pass # Decorator handles the logic

class Circle(Shape):
    def __init__(self, radius, **kwargs):
        print(f"Creating Circle with radius {radius}")
        self.radius = radius

class Square(Shape):
    def __init__(self, side, **kwargs):
        print(f"Creating Square with side {side}")
        self.side = side

# Registration (could happen automatically via metaclass or explicitly)
Shape._registry['circle'] = Circle
Shape._registry['square'] = Square


circle = Shape.create_shape(shape_type='circle', radius=5)
square = Shape.create_shape(shape_type='square', side=4)
```
