---
title: "Parameterized Decorators"
slug: parameterized-decorators
chapter: 9
book: "Fluent Python"
type: code-heavy
depends_on:
  - implementing-decorators
tags:
  - decorators
  - decorator-factory
  - parameterized
  - class-based-decorator
  - python
---

# Parameterized Decorators

## The Nesting Problem

When Python sees `@decorator`, it passes the decorated function as the first argument. So how do you pass **configuration arguments** to a decorator?

Answer: you write a **decorator factory** -- a function that takes configuration arguments and returns the actual decorator.

## Three-Level Nesting

```python
def factory(config_arg):        # Level 1: factory (takes config)
    def decorator(func):        # Level 2: actual decorator (takes function)
        def wrapper(*args):     # Level 3: replacement function
            # use config_arg, func, and args
            return func(*args)
        return wrapper
    return decorator

@factory("my_config")   # factory() returns decorator; decorator is applied to my_fn
def my_fn():
    ...
```

Key: `@factory("my_config")` first **calls** `factory("my_config")`, which returns `decorator`. Then `decorator` is applied to `my_fn`.

## Example: Parameterized Registration

```python
registry = set()

def register(active=True):
    def decorate(func):
        if active:
            registry.add(func)
        else:
            registry.discard(func)
        return func
    return decorate

@register(active=False)  # f1 NOT registered
def f1(): ...

@register()              # f2 registered (note: must use () even for defaults!)
def f2(): ...
```

Important: even with default arguments, you **must call** the factory: `@register()`, not `@register`.

## Example: Parameterized Clock

```python
import time

DEFAULT_FMT = '[{elapsed:0.8f}s] {name}({args}) -> {result}'

def clock(fmt=DEFAULT_FMT):
    def decorate(func):
        def clocked(*_args):
            t0 = time.perf_counter()
            _result = func(*_args)
            elapsed = time.perf_counter() - t0
            name = func.__name__
            args = ', '.join(repr(arg) for arg in _args)
            result = repr(_result)
            print(fmt.format(**locals()))
            return _result
        return clocked
    return decorate

@clock('{name}: {elapsed:.4f}s')
def snooze(seconds):
    time.sleep(seconds)
```

## Class-Based Alternative

A class with `__init__` and `__call__` can replace the triple nesting with a clearer structure:

```python
class clock:
    def __init__(self, fmt=DEFAULT_FMT):
        self.fmt = fmt               # __init__ stores config

    def __call__(self, func):        # __call__ IS the decorator
        def clocked(*_args):
            t0 = time.perf_counter()
            _result = func(*_args)
            elapsed = time.perf_counter() - t0
            name = func.__name__
            args = ', '.join(repr(arg) for arg in _args)
            result = repr(_result)
            print(self.fmt.format(**locals()))
            return _result
        return clocked
```

Usage is identical: `@clock()` or `@clock('{name}: {elapsed:.4f}s')`.

### Why Prefer the Class-Based Approach?

- Only two levels of indentation instead of three.
- `self.fmt` is clearer than a free variable `fmt` in a triple closure.
- Easier to add methods (e.g., for configuration changes after decoration).
- Recommended by experts like Lennart Regebro and Graham Dumpleton.

## Mental Model

| Expression | What happens |
|---|---|
| `@decorator` | `func = decorator(func)` |
| `@factory(args)` | `decorator = factory(args)` then `func = decorator(func)` |
| `@ClassName(args)` | `instance = ClassName(args)` then `func = instance(func)` (calls `__call__`) |

## See Also

- [[decorator-fundamentals]] -- simple decorators without parameters
- [[implementing-decorators]] -- the standard wrapper pattern used inside parameterized decorators
- [[functools-cache-lru-cache]] -- `@lru_cache(maxsize=N)` is a parameterized decorator from the stdlib
