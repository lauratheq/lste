#!/usr/bin/python3

"""
This module defines the `Hooks` class, which provides a flexible mechanism for managing
and executing hooks with associated callbacks. 

The `Hooks` class supports the registration of hooks with specific names, priorities, 
and callback functions. Hooks can be executed or applied in order of their priority to 
perform actions or modify values.

Classes:
    Hooks: A class that manages hooks with associated callbacks and priorities.

Usage Example:
    from hooks import Hooks

    def example_callback(value, extra_arg):
        return f"{value} modified with {extra_arg}"

    hooks = Hooks()
    hooks.add("example-hook", example_callback, priority=5)
    result = hooks.apply("example-hook", "initial value", "extra arg")
    print(result)  # Output: "initial value modified with extra arg"

    def another_callback(arg1, arg2):
        print(f"Callback with {arg1} and {arg2}")

    hooks.add("print-hook", another_callback, priority=10)
    hooks.exec("print-hook", "arg1", "arg2")  # Output: Callback with arg1 and arg2
"""

from typing import Callable, Any, Dict, List

class Hooks:
    """
    A class that manages hooks with associated callbacks and priorities.

    This class allows for the registration of hooks with specific callback functions and priorities. 
    Hooks can be applied or executed in order of their priority to modify values or perform actions.

    Attributes:
        hooks (Dict[int, List[Dict[str, Any]]]): A dictionary where keys are priorities (integers),
            and values are lists of hook dictionaries. Each hook dictionary contains:
            - 'name': The name of the hook (str)
            - 'callback': The callback function to be called (Callable[..., Any])
            - 'priority': The priority of the hook (int)

    Methods:
        add(name: str, callback: Callable[..., Any], priority: int = 10) -> None:
            Registers a new hook with the specified name, callback, and priority.

        apply(hook_name: str, initial_value: Any, *args, **kwargs) -> Any:
            Applies all hooks with the specified name to modify the initial value in order of their priority.

        exec(hook_name: str, *args, **kwargs) -> None:
            Executes all hooks with the specified name in order of their priority.
    """
    hooks: Dict[int, List[Dict[str, Any]]] = {}

    def __init__(self):
        """
        Initializes a new Hooks instance with an empty dictionary of hooks.

        The dictionary is organized by priority, with each priority containing a list of hook dictionaries.
        """
        self.hooks = {}

    def add(self, name: str, callback: Callable[..., Any], priority: int = 10) -> None:
        """
        Registers a new hook

        This method appends a new hook to the list of hooks associated with the given priority.
        Each hook is represented as a dictionary containing its name, callback function, and priority.

        Args:
            name (str): The name of the hook.
            callback (Callable[..., Any]): The callback function to be called when the hook is triggered.
            priority (int): The priority of the hook. Hooks with lower priority values are considered higher priority.
        
        Returns:
            None
        """
        hook = {
            'name': name,
            'callback': callback,
            'priority': priority
        }
        if priority in self.hooks:
            self.hooks[priority].append(hook)
        else:
            self.hooks[priority] = [hook]

    def apply(self, hook_name: str, initial_value: Any, *args, **kwargs) -> Any:
        """
        Apply all hooks with the specified name in order of their priority to modify the initial value.

        This method finds all hooks with the given name and calls their callback functions
        in ascending order of their priority. Each callback function modifies the initial value,
        and the final modified value is returned.

        Args:
            initial_value (Any): The initial value to be modified by the callbacks.
            hook_name (str): The name of the hook to apply.
            *args: Variable length argument list to pass to the callback functions.
            **kwargs: Arbitrary keyword arguments to pass to the callback functions.

        Returns:
            Any: The final modified value after applying all the callbacks.
        """
        sorted_priorities = sorted(self.hooks.keys())
        value = initial_value

        for priority in sorted_priorities:
            for hook in self.hooks[priority]:
                if hook['name'] == hook_name:
                    callback = hook['callback']
                    # Get the number of arguments the callback expects
                    num_args = callback.__code__.co_argcount - 1  # Subtract 1 for 'self'
                    # Call the callback with the current value and any additional arguments
                    if num_args == 1:  # Only one additional argument expected
                        value = callback(value, *args[:num_args], **kwargs)
                    elif num_args > 1:  # Multiple additional arguments expected
                        value = callback(value, *args[:num_args], **kwargs)
                    else:  # No additional arguments expected
                        value = callback(value)

        return value

    def exec(self, hook_name: str, *args, **kwargs) -> None:
        """
        Execute all hooks with the specified name in order of their priority.

        This method finds all hooks with the given name and calls their callback functions
        in ascending order of their priority, passing any additional arguments to the callbacks.

        Args:
            hook_name (str): The name of the hook to execute.
            *args: Variable length argument list to pass to the callback functions.
            **kwargs: Arbitrary keyword arguments to pass to the callback functions.

        Returns:
            None
        """
        # Sort hooks by priority
        sorted_hooks = sorted(self.hooks.keys())
        for priority in sorted_hooks:
            for hook in self.hooks[priority]:
                if hook['name'] == hook_name:
                    # Check the number of arguments the callback expects
                    callback = hook['callback']
                    callback_args = callback.__code__.co_argcount - 1  # Subtract 1 for 'self'
                    if callback_args == len(args):
                        callback(*args, **kwargs)
                    else:
                        callback(*args[:callback_args], **kwargs)