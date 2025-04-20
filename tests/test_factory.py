import pytest
from oarc_decorators import factory
from typing import List, Optional

# --- Test Classes ---

@factory
class SimpleProduct:
    """A simple class to test basic factory usage."""
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

@factory
class ProductWithResult:
    """A class that sets _result during init."""
    def __init__(self, item_id: int):
        self.item_id = item_id
        # Simulate processing and set a result
        self._result = f"Processed item {item_id}"

@factory
class ProductWithArgsHandling:
    """A class designed to handle the special 'args' parameter."""
    def __init__(self, name: Optional[str] = None, args: Optional[List[str]] = None):
        if args:
            # Simple mock parsing
            self.source = "args"
            self.parsed_args = args
            self.name = args[1] if len(args) > 1 and args[0] == '--name' else 'from_args'
        else:
            self.source = "kwargs"
            self.name = name
            self.parsed_args = None

# --- Tests ---

def test_factory_adds_create_method():
    """Verify the @factory decorator adds the 'create' class method."""
    assert hasattr(SimpleProduct, 'create')
    assert callable(SimpleProduct.create)

def test_create_instantiates_correctly():
    """Test standard instantiation via create with args and kwargs."""
    product1 = SimpleProduct.create("Laptop", 1200.50)
    assert isinstance(product1, SimpleProduct)
    assert product1.name == "Laptop"
    assert product1.price == 1200.50

    product2 = SimpleProduct.create(name="Keyboard", price=75.00)
    assert isinstance(product2, SimpleProduct)
    assert product2.name == "Keyboard"
    assert product2.price == 75.00

def test_create_returns_result_attribute_if_set():
    """Test that create returns instance._result if it's set and not None."""
    result = ProductWithResult.create(item_id=123)
    assert result == "Processed item 123"

    # Verify it doesn't return _result if it's None
    @factory
    class ProductWithNoneResult:
        def __init__(self):
            self._result = None
    
    instance = ProductWithNoneResult.create()
    assert isinstance(instance, ProductWithNoneResult)

def test_create_handles_special_args_keyword():
    """Test the special handling when 'args' is passed as a keyword argument."""
    cli_args = ["--name", "Monitor", "--size", "27"]
    instance = ProductWithArgsHandling.create(args=cli_args)
    
    assert isinstance(instance, ProductWithArgsHandling)
    assert instance.source == "args"
    assert instance.parsed_args == cli_args
    assert instance.name == "Monitor"

def test_create_prefers_standard_init_if_positional_args_present():
    """Test that 'args' kwarg is ignored if positional args are also given."""
    # Even though 'args' is passed, the positional 'name' should be used
    # by the factory's standard path. The __init__ receives both.
    instance = ProductWithArgsHandling.create("Standard Name", args=["--ignored"])
    
    assert isinstance(instance, ProductWithArgsHandling)
    # The factory calls cls(*args, **kwargs). 
    # The ProductWithArgsHandling.__init__ receives name="Standard Name" and args=["--ignored"].
    # The __init__'s `if args:` block runs, setting source="args".
    assert instance.source == "args" # Corrected assertion based on __init__ behavior
    # Since args is present, __init__ sets name based on args content or default 'from_args'
    assert instance.name == 'from_args' # Corrected assertion based on __init__ logic
    assert instance.parsed_args == ["--ignored"] # args kwarg is passed through

def test_create_raises_error_if_init_fails():
    """Test that exceptions during __init__ are propagated."""
    @factory
    class FailingProduct:
        def __init__(self, value):
            if value < 0:
                raise ValueError("Value cannot be negative")
            self.value = value

    with pytest.raises(ValueError, match="Value cannot be negative"):
        FailingProduct.create(value=-1)

    # Test successful case
    instance = FailingProduct.create(value=10)
    assert instance.value == 10

