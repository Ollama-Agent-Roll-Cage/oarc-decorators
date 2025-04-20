import pytest
from oarc_decorators import singleton
import click # Used by singleton for warnings

# --- Test Classes ---

@singleton
class SimpleSingleton:
    """Class with no __init__ args."""
    def __init__(self):
        self.initialized_count = getattr(self, 'initialized_count', 0) + 1
        self.value = "simple"

@singleton
class SingletonWithArgs:
    """Class with __init__ args."""
    def __init__(self, arg1, kwarg1="default"):
        self.initialized_count = getattr(self, 'initialized_count', 0) + 1
        self.arg1 = arg1
        self.kwarg1 = kwarg1

@singleton
class SingletonWithOnlyKwargs:
    """Class with only keyword args."""
    def __init__(self, *, setting="A"):
        self.initialized_count = getattr(self, 'initialized_count', 0) + 1
        self.setting = setting

# --- Fixtures ---

@pytest.fixture(autouse=True)
def reset_singletons():
    """Automatically reset singletons before and after each test."""
    # Before test
    if hasattr(SimpleSingleton, '_reset_singleton'):
        SimpleSingleton._reset_singleton()
    if hasattr(SingletonWithArgs, '_reset_singleton'):
        SingletonWithArgs._reset_singleton()
    if hasattr(SingletonWithOnlyKwargs, '_reset_singleton'):
        SingletonWithOnlyKwargs._reset_singleton()
    
    yield # Run the test

    # After test
    if hasattr(SimpleSingleton, '_reset_singleton'):
        SimpleSingleton._reset_singleton()
    if hasattr(SingletonWithArgs, '_reset_singleton'):
        SingletonWithArgs._reset_singleton()
    if hasattr(SingletonWithOnlyKwargs, '_reset_singleton'):
        SingletonWithOnlyKwargs._reset_singleton()

# --- Tests ---

def test_singleton_returns_same_instance():
    """Verify multiple instantiations return the same object."""
    instance1 = SimpleSingleton()
    instance2 = SimpleSingleton()
    assert instance1 is instance2
    assert instance1.value == "simple"

def test_singleton_init_called_once():
    """Verify __init__ is effectively called only on the first instantiation."""
    instance1 = SimpleSingleton()
    assert instance1.initialized_count == 1
    instance2 = SimpleSingleton()
    assert instance1 is instance2
    # __init__ should not run again on the instance
    assert instance1.initialized_count == 1 
    assert instance2.initialized_count == 1

def test_singleton_get_instance_method():
    """Test the added get_instance class method."""
    instance1 = SimpleSingleton()
    instance2 = SimpleSingleton.get_instance()
    assert instance1 is instance2

def test_singleton_get_instance_creates_if_not_exists():
    """Test get_instance creates the instance if called first."""
    instance = SimpleSingleton.get_instance()
    assert isinstance(instance, SimpleSingleton)
    assert instance.initialized_count == 1
    instance2 = SimpleSingleton() # Should return the same instance
    assert instance is instance2
    assert instance.initialized_count == 1

def test_singleton_with_args_same_instance():
    """Test singleton behavior with a class taking arguments."""
    instance1 = SingletonWithArgs("val1", kwarg1="kw1")
    instance2 = SingletonWithArgs("val1", kwarg1="kw1") # Same args
    instance3 = SingletonWithArgs("other_val") # Different args
    
    assert instance1 is instance2 is instance3
    assert instance1.arg1 == "val1" # Original value preserved
    assert instance1.kwarg1 == "kw1"

def test_singleton_with_args_init_called_once():
    """Verify __init__ is called once for class with args."""
    instance1 = SingletonWithArgs("val1", kwarg1="kw1")
    assert instance1.initialized_count == 1
    instance2 = SingletonWithArgs("other_val")
    assert instance1 is instance2
    assert instance1.initialized_count == 1 # Not incremented

def test_singleton_warning_on_different_args(capsys):
    """Verify warning is printed when subsequent calls use different args."""
    instance1 = SingletonWithArgs("val1", kwarg1="kw1")
    
    # Capture stdout/stderr
    captured = capsys.readouterr() 
    assert "WARNING" not in captured.out
    assert "WARNING" not in captured.err # click.secho might go to err or out

    instance2 = SingletonWithArgs("val2", kwarg1="kw2") # Different args
    
    captured = capsys.readouterr()
    # Check stderr first, then stdout as click's behavior can vary
    output = captured.err + captured.out 
    assert "WARNING: Requested SingletonWithArgs instance with different parameters" in output
    # Check specific diffs (order might vary)
    assert "arg1=val2 (was val1)" in output or "kwarg1=kw2 (was kw1)" in output
    assert "kwarg1=kw2 (was kw1)" in output or "arg1=val2 (was val1)" in output
    assert instance1 is instance2
    assert instance1.arg1 == "val1" # Original args preserved

def test_singleton_warning_on_different_kwargs_only(capsys):
    """Verify warning for classes with only keyword arguments."""
    instance1 = SingletonWithOnlyKwargs(setting="B")
    captured = capsys.readouterr()
    assert "WARNING" not in (captured.err + captured.out)

    instance2 = SingletonWithOnlyKwargs(setting="C") # Different kwarg
    captured = capsys.readouterr()
    output = captured.err + captured.out
    assert "WARNING: Requested SingletonWithOnlyKwargs instance with different parameters" in output
    assert "setting=C (was B)" in output
    assert instance1 is instance2
    assert instance1.setting == "B" # Original setting preserved

def test_singleton_reset_method():
    """Test the _reset_singleton class method."""
    instance1 = SimpleSingleton()
    SimpleSingleton._reset_singleton()
    instance2 = SimpleSingleton()
    
    assert instance1 is not instance2
    assert isinstance(instance2, SimpleSingleton)
    assert instance2.initialized_count == 1 # Re-initialized

def test_singleton_works_with_no_args_init():
    """Explicitly test class with __init__(self)."""
    @singleton
    class NoArgsInit:
        def __init__(self):
            self.x = 10
    
    i1 = NoArgsInit()
    i2 = NoArgsInit()
    assert i1 is i2
    assert i1.x == 10

# Test interaction with inheritance (basic check)
def test_singleton_inheritance():
    """Check if singleton works correctly with inherited classes."""
    class Base:
        def __init__(self, base_arg):
            self.base_arg = base_arg

    @singleton
    class Derived(Base):
        def __init__(self, base_arg, derived_arg):
            super().__init__(base_arg)
            self.derived_arg = derived_arg
            self.init_count = getattr(self, 'init_count', 0) + 1

    d1 = Derived("base1", "derived1")
    d2 = Derived("base2", "derived2") # Different args

    assert d1 is d2
    assert d1.base_arg == "base1"
    assert d1.derived_arg == "derived1"
    assert d1.init_count == 1

