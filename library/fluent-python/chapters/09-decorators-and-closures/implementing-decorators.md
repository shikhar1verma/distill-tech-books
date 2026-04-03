---
title: "Implementing a Well-Behaved Decorator"
slug: implementing-decorators
chapter: 9
book: "Fluent Python"
type: code-heavy
depends_on:
  - nonlocal-declaration
tags:
  - decorators
  - functools.wraps
  - wrapper-pattern
  - python
---

# Implementing a Well-Behaved Decorator

## The Pattern

Most decorators follow this template:

```python
import functools

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # ... do something before ...
        result = func(*args, **kwargs)
        # ... do something after ...
        return result
    return wrapper
```

### Key elements:

1. **`*args, **kwargs`** -- the wrapper accepts any arguments so it works with any decorated function.
2. **`func` in the closure** -- the original function is captured as a free variable.
3. **`@functools.wraps(func)`** -- copies `__name__`, `__doc__`, `__module__`, `__qualname__`, `__annotations__`, and `__dict__` from `func` to `wrapper`.

## Example: A Clock Decorator

```python
import time
import functools

def clock(func):
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        name = func.__name__
        arg_lst = [repr(arg) for arg in args]
        arg_lst.extend(f'{k}={v!r}' for k, v in kwargs.items())
        print(f'[{elapsed:0.8f}s] {name}({", ".join(arg_lst)}) -> {result!r}')
        return result
    return clocked
```

## Why functools.wraps Matters

Without `@functools.wraps`, the decorated function loses its identity:

```python
@clock
def factorial(n):
    """Compute n!"""
    return 1 if n < 2 else n * factorial(n - 1)

# Without wraps:
factorial.__name__  # 'clocked'  <-- wrong!
factorial.__doc__   # None       <-- lost!

# With wraps:
factorial.__name__  # 'factorial'
factorial.__doc__   # 'Compute n!'
```

This matters for debugging, introspection, documentation generation, and any tool that inspects function metadata.

## How It Works Under the Hood

When `@clock` is applied to `factorial`:

1. Python calls `clock(factorial)`, which returns `clocked`.
2. The name `factorial` is rebound to `clocked`.
3. Every call to `factorial(n)` now executes `clocked(n)`.
4. Inside `clocked`, `func` (the original `factorial`) is called via the closure.

For recursive functions like `factorial`, the recursion goes through the wrapper on each call because `factorial` now points to `clocked`.

## Stacked Decorators

Multiple decorators are applied bottom-up:

```python
@alpha
@beta
def my_fn():
    ...

# equivalent to:
my_fn = alpha(beta(my_fn))
```

`beta` is applied first; its return value is passed to `alpha`.

## See Also

- [[functools-cache-lru-cache]] -- a standard library decorator that uses this pattern
- [[parameterized-decorators]] -- adding configuration arguments to your decorators
