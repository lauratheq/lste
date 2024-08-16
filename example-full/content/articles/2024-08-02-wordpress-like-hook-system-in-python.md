{{active-menu: blog}}
{{category: Python}}
{{title: Working-Directory - WordPress-like Hook System in Python}}
{{keywords: wordpress, python}}

# WordPress-like Hook System in Python

One of WordPress’s standout features is its Hook System, which allows developers to execute actions and filter variables seamlessly. Inspired by this, I decided to implement a similar plugin system within my Python tools. To my surprise, the process was remarkably straightforward.

If you want to skip the explaination and just want to see the full implementation just follow this [link to the gist](https://gist.github.com/lauratheq/ef6adfc57cfba93d9d7c98a1b90843a6).

## Understanding Hooks: A Practical Example

In programming, hooks are powerful tools that allow we to extend or modify the behavior of a system without altering its core code. Let’s dive into how this concept can be applied in Python with a practical example.

Consider the fdummy function, which contains a title:

```
def get_title(self):
    title = "Foobar"
    return title

title = get_title
```

In this setup, the `title` variable is assigned a value from the `get_title` function. However, as it stands, there’s no way to manipulate or extend the value of title beyond the default implementation.

This is where hooks come into play. With a hook system, we can insert custom functions to modify or enhance the behavior of existing methods. For example, we could create a hook that allows external code to change the title before it's set, adding flexibility and customization options to our class.

## The anatomy of a hook

In a hook system, each hook comprises three fundamental components: the name, the callback function, and the priority:

### 1. Name of the Hook

The name of a hook acts as an identifier or label. It allows us to group and manage related hooks under a common name. This is particularly useful if we want to apply or execute all hooks associated with a specific functionality. For example, if we have multiple ways to modify a title, we might name our hooks "modify-title".

### 2. Callback Function

The callback function is the heart of the hook. It contains the logic that should be executed when the hook is triggered. Callbacks can be used to modify values, perform actions, or integrate additional functionality. When we register a hook, we specify the callback function that will be called with the hook’s parameters.

For instance, a callback might take an initial value and some additional arguments to transform the value:

```
def modify_title(value, extra_arg):
    return f"{value} - {extra_arg}"
```

### 3. Priority

The priority determines the order in which hooks are executed. Hooks with lower priority values are executed before those with higher values. This allows us to control the sequence of operations, ensuring that hooks affecting the same variable or process are applied in a specific order.

For example, if we have two hooks that modify a title, we might set different priorities to control which modification happens first. If the priority is the same in each hook, we execute it by what comes first:

```
hooks.add("modify-title", modify_title, priority=5)
hooks.add("modify-title", another_callback, priority=10)
```

In this setup, `modify_title` will be applied before `another_callback` because it has a lower priority value.

### Putting It All Together
When we register a hook, we combine these three elements to create a mechanism that can be executed or applied later. Here’s a quick example of how a hook is defined and used:

```
def example_callback(value, extra_arg):
    return f"{value} modified with {extra_arg}"

hooks.add("example-hook", example_callback, priority=5)
```

In this case:

* **Name:** "example-hook"
* **Callback:** example_callback
* **Priority:** 5

When we apply this hook with an initial value, the `example_callback` function will be executed with the provided arguments, modifying the value according to its logic and priority.

## Implementation of the Hook-Class: the add method

The `Hooks` class is designed to manage and organize hooks efficiently. Here’s how it achieves this using Python’s built-in data structures:

### 1. Data Structure:

The class uses a dictionary named hooks to store hooks. The structure is as follows:

```
hooks: Dict[int, List[Dict[str, Any]]] = {}
```

* **Key:** The keys in the hooks dictionary are integers representing the priority of the hooks.
* **Value:** The values are lists of dictionaries. Each dictionary represents a hook and contains the following details:
 * **'name':** The name of the hook (a string).
 * **'callback':** The function to be called when the hook is triggered (a callable).
 * **'priority':** The priority of the hook (an integer).

### 2. Initialization:

In the `__init__` method, the hooks dictionary is initialized as an empty dictionary:

```
def __init__(self):
    self.hooks = {}
```

This sets up a fresh instance of the Hooks class with no hooks registered initially.

### 3. Adding Hooks:

When we add a hook using the add method, the hook is stored in the hooks dictionary based on its priority:

```
def add(self, name: str, callback: Callable[..., Any], priority: int = 10) -> None:
    hook = {
        'name': name,
        'callback': callback,
        'priority': priority
    }
    if priority in self.hooks:
        self.hooks[priority].append(hook)
    else:
        self.hooks[priority] = [hook]
```

Here’s a step-by-step breakdown of this method:

1. Creating a Hook Dictionary:
 * A hook is defined as a dictionary with 'name', 'callback', and 'priority' keys.
Storing the Hook:
2. The if priority in self.hooks check determines if there are already hooks with the specified priority.
 * If hooks with this priority exist, the new hook is appended to the existing list.
 * If no hooks with this priority exist, a new list is created with the new hook as its first item.

## Implementation of the Hook-Class: the apply method

The apply method in the Hooks class is responsible for applying all registered hooks with a specific name to an initial value. Here's how it works:

```
def apply(self, hook_name: str, initial_value: Any, *args, **kwargs) -> Any:
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
```

### Sorting Priorities:

```
sorted_priorities = sorted(self.hooks.keys())
```

Hooks are organized by priority, and the priorities are sorted in ascending order. This ensures that hooks with lower priority values are executed first.

### Initializing the Value:

```
value = initial_value
```

The `initial_value` is set to the value variable, which will be modified by the hooks.

### Iterating Through Priorities and Hooks:

```
for priority in sorted_priorities:
    for hook in self.hooks[priority]:
        if hook['name'] == hook_name:
            callback = hook['callback']
```

The method iterates over each priority level in ascending order. For each priority, it checks all hooks.
It then filters the hooks to find those that match the specified `hook_name`.

### Determining the Number of Arguments:

```
num_args = callback.__code__.co_argcount - 1
```

The number of arguments expected by the callback function is determined using `callback.__code__.co_argcount`, minus one to account for the implicit self parameter in instance methods.

### Calling the Callback Function:

*Single Argument Case:*

```
if num_args == 1:
    value = callback(value, *args[:num_args], **kwargs)
```

If the callback expects only one additional argument, the method calls it with the current value and any additional arguments provided.

*Multiple Arguments Case:*

```
elif num_args > 1:
    value = callback(value, *args[:num_args], **kwargs)
```

If the callback expects multiple arguments, it calls the callback similarly, handling the expected number of arguments`

*No Additional Arguments:*

```
else:
    value = callback(value)
```

If the callback does not expect additional arguments, it is called with just the current value. After all applicable hooks have been executed, the final modified value is returned.

Why This Method Is Useful:

* Sequential Application: By processing hooks in order of their priority, the method ensures that hooks with higher importance (lower priority values) are applied first.
* Flexible Callback Execution: The method dynamically handles callbacks with varying numbers of arguments, making it adaptable to different hook implementations.
* Value Transformation: This approach allows us to progressively transform an initial value through a series of hooks, enabling complex modifications in a controlled manner.

## Example Usage

And that's basically everything we need. Let’s apply this to our example:

```
from hooks import Hooks

# Define a callback function to modify the title
def modify_title(value, extra_arg):
    return f"{value} - {extra_arg}"

# Create an instance of the Hooks class
hooks = Hooks()

# Add a hook with a specific priority
hooks.add("modify-title", modify_title, priority=5)

# Apply hooks to modify an initial value
result = hooks.apply("modify-title", "Original Title", "Extra Info")
print(result)  # Output: "Original Title - Extra Info"
```

* **Adding Hooks:** The add method registers hooks by specifying their name, callback function, and priority. Hooks with lower priority values are executed first.
* **Applying Hooks:** The apply method executes all hooks with the given name, modifying an initial value based on their priority. This is useful for transforming data before final use.
* **Executing Hooks:** The exec method triggers all hooks with the specified name, allowing them to perform actions in the order of their priority.

If you want to play with that system, you can find the whole class in this [gist](https://gist.github.com/lauratheq/ef6adfc57cfba93d9d7c98a1b90843a6).