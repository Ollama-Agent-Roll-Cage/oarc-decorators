"""
OARC Singleton Decorator

This module provides a robust singleton decorator for Python classes.
It ensures that only one instance of a decorated class exists, regardless
of how many times the class is instantiated. The decorator supports
initialization arguments, tracks and warns about parameter mismatches
on subsequent instantiations, and provides utility methods for testing
and explicit instance retrieval.

Features:
- Guarantees a single instance per decorated class.
- Tracks initialization arguments and warns if subsequent calls differ.
- Provides `get_instance()` and `reset_singleton()` class methods for
    explicit instance management and testing.
- Uses informative logging via `click.secho` for warnings and diagnostics.
"""

from typing import Type, TypeVar, Dict, Any
import functools
import inspect

import click

T = TypeVar('T')

# Dictionary to store singleton instances by class
_instances: Dict[Type, Any] = {}


def singleton(cls: Type[T]) -> Type[T]:
    """
    Singleton decorator for classes.

    Ensures only one instance of the decorated class exists.
    Tracks initialization arguments and warns if subsequent instantiations
    use different parameters. Provides utility methods for explicit instance
    management and testing.

    Args:
        cls: The class to decorate as a singleton.

    Returns:
        The decorated class with singleton behavior.
    """

    original_init = cls.__init__
    original_new = cls.__new__
    
    try:
        # Get the parameter names from the original __init__ method
        init_signature = inspect.signature(original_init)
        param_names = [p for p in init_signature.parameters if p != 'self']
    except (ValueError, TypeError) as e:
        # Handle case where signature cannot be inspected
        click.secho(f"WARNING: Could not inspect signature for {cls.__name__}: {e}", fg='yellow')
        param_names = []
    

    @functools.wraps(original_new)
    def __new__(cls, *args, **kwargs):
        if cls not in _instances:
            instance = original_new(cls)
            # Initialize tracking attributes before any other initialization
            instance._init_args = ()
            instance._init_kwargs = {}
            instance._initialized = False
            _instances[cls] = instance
            return instance
        return _instances[cls]
    

    @functools.wraps(original_init)
    def __init__(self, *args, **kwargs):
        # Check if this instance has already been initialized
        if not self._initialized:
            # Proceed with the original initialization logic
            original_init(self, *args, **kwargs)
            
            # Store initialization parameters for comparison
            self._init_args = args
            self._init_kwargs = kwargs
            self._initialized = True
        else:
            # Check if initialization parameters differ and log a warning if they do
            if args != self._init_args or kwargs != self._init_kwargs:
                # Create a more informative message about the parameter differences
                new_params = {}
                old_params = {}
                
                # Combine positional and keyword arguments
                for i, param_name in enumerate(param_names):
                    if i < len(args):
                        new_params[param_name] = args[i]
                    if i < len(self._init_args):
                        old_params[param_name] = self._init_args[i]
                
                # Add keyword arguments
                new_params.update(kwargs)
                old_params.update(self._init_kwargs)
                
                # Find differences
                diff_params = []
                for key in set(new_params.keys()) | set(old_params.keys()):
                    if key in new_params and key in old_params and new_params[key] != old_params[key]:
                        diff_params.append(f"{key}={new_params[key]} (was {old_params[key]})")
                    elif key in new_params and key not in old_params:
                        diff_params.append(f"{key}={new_params[key]} (was not set)")
                    elif key not in new_params and key in old_params:
                        diff_params.append(f"{key} not set (was {old_params[key]})")
                
                if diff_params:
                    diff_str = ", ".join(diff_params)
                    click.secho(f"WARNING: Requested {cls.__name__} instance with different parameters: {diff_str}. "
                               f"Using existing instance with original parameters.", fg='yellow')
    

    # Replace the class methods
    cls.__new__ = __new__
    cls.__init__ = __init__
    

    # Add a custom reset method for testing and cleanup
    def reset_singleton(cls):
        """
        Remove the singleton instance, allowing a new one to be created.

        This is primarily intended for testing or resetting the singleton state.
        """
        if cls in _instances:
            del _instances[cls]
    
    cls.reset_singleton = classmethod(reset_singleton)
    
    # Add get_instance classmethod to explicitly get the singleton instance
    @classmethod
    def get_instance(cls_):
        """
        Retrieve the singleton instance of the class.

        If the instance does not exist, it will be created using the default
        constructor arguments. This method is the preferred way to access the
        singleton instance explicitly, without directly invoking the class.

        Returns:
            The singleton instance of the class.
        """
        # cls_ refers to the decorated class itself when called as ClassName.get_instance()
        if cls_ not in _instances:
            return cls_()
        return _instances[cls_]
    
    # Add the get_instance method to the class
    cls.get_instance = get_instance
    
    return cls
