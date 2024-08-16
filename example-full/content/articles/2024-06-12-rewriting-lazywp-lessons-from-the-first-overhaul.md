{{active-menu: blog}}
{{category: lazywp}}
{{title: Working-Directory - Rewriting LazyWP: Lessons from the First Overhaul}}
{{keywords: lazywp, wordpress, python}}

# Rewriting LazyWP: Lessons from the First Overhaul

A couple of weeks ago, I embarked on a journey to develop LazyWP, a tool that leverages curses and Python to create a terminal user interface for WordPress users. As any developer knows, the first iteration of a software project is rarely perfect, and mine was no exception. After some initial development, I found myself at a crossroads that many developers face: it was time for a rewrite.

This rewrite was a profound learning experience. I quickly discovered the importance of starting on a smaller scale before diving into full-scale implementation of features. By focusing on creating a solid foundation, I ensured that the core functionalities were robust and maintainable. This approach not only made the development process smoother but also enhanced my understanding of [curses](https://docs.python.org/3/library/curses.html) and object-oriented programming in Python.

To be more specific, I restructured the entire codebase and created methods that are much more logical and organized. Now, the code is (more or less) fully documented—a step I initially underestimated but found immensely helpful in the development process. Additionally, I implemented a pseudo-MVC pattern, which gathers all the necessary information and content beforehand, then efficiently displays it.

One of the key points in rewriting the code was the implementation of commands. It’s possible to develop dynamic imports for packages and call methods within those packages. This makes it surprisingly easy to create new implementations of wpcli commands, as seen in the [plugins](https://github.com/lauratheq/lazywp/blob/main/src/commands/plugins.py) implementation. I aimed to make everything as clean and understandable as possible so others could adapt and contribute. However, I’m not entirely sure if my approach to dynamic package loading is correct. It seems straightforward, but Python’s intricacies can be tricky, and I’m still learning. Nonetheless, these [lines](https://github.com/lauratheq/lazywp/blob/main/lazywp#L161) of code are the core of the magic:

```
commands_path = self.lazywp_path + '/src/commands/'
commands = [name for _, name, _ in pkgutil.iter_modules([commands_path])]
for command in commands:
    self.log.debug(f" - {command}")
    command_package = importlib.import_module('src.commands.'+command)
    self.commands_modules[command] = command_package
    command_config = command_package.config()
    self.commands[command] = command_config
```

Anyway, I can now check off some items on my to-do list for this project:

*   Display help which aggregates the infos from the commands (press \[?\])
*   Methods to make usage of curses easier within the project
    *   Tables
    *   Modals
    *   Confirmation Boxes
    *   Alerts
*   Code comments (I am proud!)
*   Plugins
    *   toggle auto update
    *   installation of new plugins
*   Themes
    *   update
    *   update all
    *   activate
    *   deactivate
    *   toggle auto update
    *   install
    *   remove

I’ve put together a small video of the current state:

lazywp demonstration

When I installed the “default” theme, LazyWP stopped working because wpcli threw numerous PHP Fatal Errors that weren’t caught anywhere. So, my next task is to check the health of the underlying WordPress installation before starting up LazyWP. I believe this will also create synergies with wpcli, as I’ve identified some related issues.

Unfortunately, I won’t have much time to work on the project in the coming months due to my upcoming bachelor thesis. If anyone is interested in contributing, please reach out! 🙂