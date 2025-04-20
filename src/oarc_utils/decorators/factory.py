"""
Factory pattern decorator for Python classes.

This module provides a class decorator that adds a `create` class method to the decorated class,
enabling flexible and consistent instantiation of objects, including support for special argument
handling and post-initialization result extraction.

Usage:
    @factory
    class MyClass:
        def __init__(self, ...):
            ...

    instance = MyClass.create(...)
"""

from typing import Any, Type, TypeVar

# Type variable for generic typing
T = TypeVar('T')


def factory(cls: Type[T]) -> Type[T]:
    """
    Class decorator that adds a flexible factory method to the decorated class.

    This decorator injects a `create` class method, enabling consistent and customizable
    instantiation of objects. It supports special argument handling (such as passing
    CLI-style arguments via an 'args' keyword) and can return a post-processed result
    if the instance defines a `_result` attribute.

    Example:
        @factory
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        # Standard instantiation:
        john = Person.create(name="John", age=30)

        # Special handling for CLI-style argument parsing:
        result = Person.create(args=["--name", "John", "--age", "30"])
    """


    @classmethod
    def create(cls_method, *args: Any, **kwargs: Any) -> Any:
        """
        Factory method to create and return a new instance of the class.

        This method provides a unified way to instantiate the class, supporting both
        standard constructor arguments and special CLI-style argument parsing via the
        'args' keyword.

        Args:
            *args: Positional arguments to pass to the class constructor.
            **kwargs: Keyword arguments to pass to the class constructor. If 'args' is
            provided as a keyword argument and no positional arguments are given,
            it will be passed directly to the constructor for special handling.

        Returns:
            An instance of the class, or the value of its '_result' attribute if present
            and not None (useful for classes that perform processing in __init__ and
            store results in '_result').
        """
        # Special handling for the 'args' parameter which is expected by _process_args
        if 'args' in kwargs and len(args) == 0:
            instance = cls(args=kwargs['args'])
            # If instance has a _result attribute, return that instead
            if hasattr(instance, '_result') and instance._result is not None:
                return instance._result
            return instance
            
        instance = cls(*args, **kwargs)
        
        # If instance has a result to return (special case for CLI args processing),
        # return that directly
        if hasattr(instance, '_result') and instance._result is not None:
            return instance._result
            
        return instance
    
    # Add the method to the class
    setattr(cls, 'create', create)
    
    return cls
