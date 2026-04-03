---
title: "Context Managers and the with Statement"
aliases: ["with statement", "context manager protocol", "__enter__", "__exit__"]
tags: [fluent-python, chapter-18, context-manager, with-statement]
chapter: 18
concept: 1
type: code-heavy
---

# Context Managers and the `with` Statement

## Core Idea

A **context manager** is any object that implements `__enter__` and `__exit__`. The `with` statement calls `__enter__` at the top of the block and guarantees that `__exit__` is called when the block finishes -- whether it completes normally, raises an exception, or exits via `return`/`break`/`continue`.

The `with` statement was designed to replace common `try/finally` patterns where some resource must be released or some state must be restored.

## The Protocol

```python
with EXPRESSION as VAR:
    BODY
```

1. Python evaluates `EXPRESSION` to get the **context manager object**.
2. Python calls `__enter__()` on the context manager. The return value is bound to `VAR`.
3. `BODY` executes.
4. Python calls `__exit__(exc_type, exc_value, traceback)` on the context manager.

**Critical distinction:** the context manager (from `EXPRESSION`) is not necessarily the same object as `VAR` (from `__enter__`). For files, `__enter__` returns `self`, but other classes may return something different.

## The `__exit__` Signature

```python
def __exit__(self, exc_type, exc_value, traceback):
```

- If the block completed normally: all three arguments are `None`.
- If an exception occurred: they hold the exception class, instance, and traceback.
- **Returning a truthy value suppresses the exception.** Returning `None` (the default) propagates it.

## Example: Custom Context Manager

```python
import sys

class LookingGlass:
    def __enter__(self):
        self.original_write = sys.stdout.write
        sys.stdout.write = self._reverse_write
        return 'JABBERWOCKY'

    def _reverse_write(self, text):
        self.original_write(text[::-1])

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout.write = self.original_write
        if exc_type is ZeroDivisionError:
            print('Please DO NOT divide by zero!')
            return True  # suppress the exception
```

## Parenthesized Context Managers (Python 3.10+)

Python 3.10 allows multiple context managers in parentheses:

```python
with (
    CtxManager1() as a,
    CtxManager2() as b,
    CtxManager3() as c,
):
    ...
```

Prior to 3.10, this required nested `with` blocks.

## Common Uses in the Standard Library

- **File I/O**: `open()` returns a CM that closes the file
- **Database transactions**: `sqlite3` connection as CM
- **Threading**: locks, conditions, and semaphores
- **Decimal arithmetic**: `decimal.localcontext` for temporary precision settings
- **Testing**: `unittest.mock.patch`

## Connections

- [[contextlib-utilities]] -- higher-level tools for building context managers
- [[contextmanager-decorator]] -- generator-based context managers with `@contextmanager`
