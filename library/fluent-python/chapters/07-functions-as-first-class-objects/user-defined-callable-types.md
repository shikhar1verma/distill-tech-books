---
title: "User-Defined Callable Types (__call__)"
book: "Fluent Python"
chapter: 7
tags: [__call__, callable, stateful-functions, python-data-model]
related:
  - "[[callable-types]]"
  - "[[first-class-functions]]"
  - "[[special-dunder-methods]]"
---

# User-Defined Callable Types (`__call__`)

## Summary

Any Python class that implements the `__call__` instance method makes its instances callable like functions. This is a powerful pattern for creating **function-like objects with persistent internal state** -- bridging the gap between functions and objects. The `callable()` built-in returns `True` for such instances.

## How It Works

```python
import random

class BingoCage:
    """A callable that pops a random item each time it's called."""

    def __init__(self, items):
        self._items = list(items)
        random.shuffle(self._items)

    def pick(self):
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError("pick from empty BingoCage")

    def __call__(self):
        return self.pick()

# Usage
bingo = BingoCage(range(3))
bingo.pick()       # e.g., 1
bingo()            # e.g., 0  — same as bingo.pick()
callable(bingo)    # True
```

Key points:
- `__call__` delegates to `self.pick()`, providing a shortcut syntax.
- `callable(bingo)` returns `True` because the class defines `__call__`.
- The instance maintains state (`self._items`) between calls.

### As a decorator

Classes with `__call__` can be used as decorators:

```python
class CallCounter:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)

@CallCounter
def greet(name):
    return f"Hello, {name}!"

greet("Alice")     # "Hello, Alice!"
greet("Bob")       # "Hello, Bob!"
greet.count        # 2
```

## In Practice

- **Stateful callbacks:** When a callback needs to remember information between invocations (e.g., caching, counting, accumulating).
- **Decorators as classes:** The `__call__` method holds the wrapper logic; `__init__` captures the decorated function and configuration.
- **Strategy pattern:** Callable objects can replace both plain functions and full strategy class hierarchies.
- **Memoization:** Store computed results in instance attributes and return cached values in `__call__`.

## Common Pitfalls

- **Forgetting `__call__` returns a value:** If `__call__` does not return, calling the instance returns `None`.
- **Using `__call__` when a closure suffices:** For simple state, a closure (inner function + `nonlocal`) is lighter weight. Use `__call__` when you need multiple methods, complex state, or introspectable attributes.
- **Decorator classes and `functools.wraps`:** When using a class as a decorator, the wrapped function loses its `__name__` and `__doc__`. Use `functools.update_wrapper(self, func)` in `__init__` to preserve them.

## See Also

- [[callable-types]] -- The nine callable types in Python
- [[first-class-functions]] -- Functions as first-class objects
- Chapter 9 covers closures (the functional alternative to `__call__` for state)
- Chapter 10 discusses design patterns simplified by callables
