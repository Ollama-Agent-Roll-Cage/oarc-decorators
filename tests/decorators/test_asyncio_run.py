import asyncio
import pytest
from oarc_utils.decorators import asyncio_run

async def simple_async_func():
    """A simple async function for testing."""
    await asyncio.sleep(0.01)
    return "done"

async def async_func_with_args(arg1, kwarg1="default"):
    """An async function with arguments."""
    await asyncio.sleep(0.01)
    return f"{arg1}-{kwarg1}"

async def async_func_raises():
    """An async function that raises an exception."""
    await asyncio.sleep(0.01)
    raise ValueError("Test exception from async func")

@pytest.fixture
def decorated_simple():
    """Fixture for the simple decorated function."""
    @asyncio_run
    async def wrapped_simple():
        return await simple_async_func()
    return wrapped_simple

@pytest.fixture
def decorated_with_args():
    """Fixture for the decorated function with arguments."""
    @asyncio_run
    async def wrapped_with_args(arg1, kwarg1="default"):
        return await async_func_with_args(arg1, kwarg1=kwarg1)
    return wrapped_with_args

@pytest.fixture
def decorated_raises():
    """Fixture for the decorated function that raises."""
    @asyncio_run
    async def wrapped_raises():
        return await async_func_raises()
    return wrapped_raises

# Test execution and return value
def test_asyncio_run_executes_and_returns(decorated_simple):
    """Verify the decorated function runs and returns the async result."""
    result = decorated_simple()
    assert result == "done"

# Test with arguments
def test_asyncio_run_with_args(decorated_with_args):
    """Verify arguments are passed correctly."""
    result1 = decorated_with_args("test_arg")
    assert result1 == "test_arg-default"

    result2 = decorated_with_args("arg1_val", kwarg1="kwarg_val")
    assert result2 == "arg1_val-kwarg_val"

# Test exception propagation
def test_asyncio_run_propagates_exception(decorated_raises):
    """Verify exceptions from the async function are raised by the wrapper."""
    with pytest.raises(ValueError, match="Test exception from async func"):
        decorated_raises()

# Test decorator preserves function metadata (basic check)
def test_asyncio_run_preserves_metadata():
    """Check if functools.wraps is working."""

    @asyncio_run
    async def original_func_for_meta():
        """Docstring for original."""
        pass

    assert original_func_for_meta.__name__ == "original_func_for_meta"
    assert "Docstring for original" in original_func_for_meta.__doc__
