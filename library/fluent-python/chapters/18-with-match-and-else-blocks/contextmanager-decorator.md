---
title: "Using @contextmanager"
aliases: ["@contextmanager", "contextmanager decorator", "generator context manager"]
tags: [fluent-python, chapter-18, contextlib, contextmanager, generator]
chapter: 18
concept: 3
type: code-heavy
---

# Using `@contextmanager`

## Core Idea

The `@contextlib.contextmanager` decorator transforms a **generator function with a single `yield`** into a full context manager. This is far more concise than writing a class with `__enter__` and `__exit__`.

- Code **before** `yield` runs on `__enter__`
- The **yielded value** is bound to the `as` variable
- Code **after** `yield` runs on `__exit__`

## Basic Pattern

```python
import contextlib

@contextlib.contextmanager
def managed_resource():
    # setup (runs on __enter__)
    resource = acquire()
    try:
        yield resource       # value for the `as` clause
    finally:
        # teardown (runs on __exit__, even on exceptions)
        resource.release()
```

## Example: `looking_glass`

```python
import contextlib
import sys

@contextlib.contextmanager
def looking_glass():
    original_write = sys.stdout.write

    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write
    msg = ''
    try:
        yield 'JABBERWOCKY'
    except ZeroDivisionError:
        msg = 'Please DO NOT divide by zero!'
    finally:
        sys.stdout.write = original_write
        if msg:
            print(msg)
```

## How It Works Internally

The decorator wraps the generator in a `_GeneratorContextManager` class:

1. **`__enter__`**: Calls the generator function to get `gen`, then calls `next(gen)` to advance to `yield`. Returns the yielded value.
2. **`__exit__`** (no exception): Calls `next(gen)` to resume after `yield`.
3. **`__exit__`** (exception): Calls `gen.throw(exception)` which raises the exception at the `yield` line.

## Critical: Wrap `yield` in `try/finally`

Without `try/finally`, if an exception is raised in the `with` block, the generator terminates at the `yield` and cleanup code never runs. **Always use `try/finally` (or a nested `with` block) around the `yield`.**

## Inverted Default Behavior

With a class-based CM, `__exit__` must return `True` to suppress exceptions. With `@contextmanager`, the behavior is **inverted**: if you catch an exception around `yield` and don't re-raise it, the exception is suppressed by default.

## Double Duty: Context Manager + Decorator

Because `@contextmanager` builds on `ContextDecorator`, the result can also be used as a **function decorator**:

```python
@looking_glass()
def verse():
    print('The time has come')

verse()   # output is reversed
```

The entire function body runs inside the managed context.

## Connections

- [[context-managers-and-with]] -- the protocol that `@contextmanager` implements
- [[contextlib-utilities]] -- the module that provides this decorator
