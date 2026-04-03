---
title: "Command Pattern with Callables"
chapter: 10
concept_slug: command-pattern-with-callables
book: "Fluent Python"
type: mixed
depends_on:
  - function-oriented-strategy
tags:
  - design-patterns
  - command-pattern
  - callable
  - dunder-call
  - macro-command
---

# Command Pattern with Callables

## The classic Command pattern

The Command pattern decouples the **invoker** (e.g., a menu item or button) from the **receiver** (the object that performs the action). A `Command` object sits between them, implementing an `execute()` method that calls the appropriate method on the receiver.

Participants:
- **Invoker**: triggers the command (e.g., a toolbar button)
- **Command**: interface with `execute()` method
- **Concrete Command**: implements `execute()`, holds a reference to the receiver
- **Receiver**: the object that does the actual work (e.g., `Document`)

## The Pythonic simplification

In Python, every **callable** already implements a single-method interface: `__call__`. Instead of a `Command` class hierarchy:

- **Simple commands**: use plain functions (or closures)
- **Compound commands**: use a `MacroCommand` class with `__call__`

```python
class MacroCommand:
    """A command that executes a list of commands"""

    def __init__(self, commands):
        self.commands = list(commands)

    def __call__(self):
        for command in self.commands:
            command()
```

## Example: editor commands

```python
doc = Document("Hello, world!")

# Commands as closures over doc
def select_all():
    doc.clipboard = doc.text

def uppercase():
    doc.text = doc.text.upper()

# MacroCommand batches them
macro = MacroCommand([uppercase, select_all])
macro()  # executes both in sequence
```

## When you still need a Command class

Not every use case is simple enough for bare functions:

| Need | Solution |
|------|----------|
| Just execute an action | Plain function |
| Batch multiple actions | `MacroCommand` with `__call__` |
| Undo support | Callable class with state, or `(do, undo)` function pairs |
| Logging / serialization | Callable class that records invocations |
| Complex state | Full Command class (but consider closures first) |

## The general principle

> "Commands are an object-oriented replacement for callbacks." -- *Design Patterns*

The question is: do we need an object-oriented replacement for callbacks in Python? Often, **no**. Functions *are* callbacks. The `__call__` protocol means any object can be a callback if needed.

This is the same insight as [[function-oriented-strategy]]: whenever a pattern requires **single-method classes with no state**, first-class functions are simpler.

## Key takeaway

The Command and Strategy patterns share a structural similarity -- both involve objects with a single method that the client invokes. In Python, both simplify to **callables**. Recognize this pattern: `execute()`, `run()`, `do_it()`, `handle()` -- any single-method interface can often be replaced by a function or `__call__`.

## See also

- [[function-oriented-strategy]] -- the same simplification applied to Strategy
- [[classic-strategy-pattern]] -- understanding why single-method classes arise in GoF patterns
