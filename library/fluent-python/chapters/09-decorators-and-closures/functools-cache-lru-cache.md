---
title: "Memoization with functools.cache and lru_cache"
slug: functools-cache-lru-cache
chapter: 9
book: "Fluent Python"
type: code-heavy
depends_on:
  - implementing-decorators
tags:
  - memoization
  - functools
  - cache
  - lru_cache
  - performance
  - python
---

# Memoization with functools.cache and lru_cache

## What is Memoization?

Memoization is an optimization that saves the results of expensive function calls and returns the cached result when the same inputs occur again. The `functools` module provides two decorators for this.

## functools.cache (Python 3.9+)

`@functools.cache` is an unbounded cache -- it stores every unique call forever.

```python
import functools

@functools.cache
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)
```

Without caching, `fibonacci(30)` makes 2,692,537 calls. With caching, it makes just 31.

### Constraints

- All arguments must be **hashable** (they are used as dict keys).
- Memory is **unbounded** -- every unique call is stored forever.
- Best suited for **short-lived scripts**, not long-running servers.

## functools.lru_cache

`@functools.lru_cache` adds bounded memory via a Least Recently Used eviction policy.

### Usage (two forms since Python 3.8):

```python
# Simple form (Python 3.8+) -- uses defaults
@functools.lru_cache
def costly_function(a, b):
    ...

# Parameterized form (Python 3.2+)
@functools.lru_cache(maxsize=256, typed=True)
def costly_function(a, b):
    ...
```

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `maxsize` | 128 | Max entries stored. Should be a power of 2 for best performance. `None` disables eviction (same as `@cache`). |
| `typed` | `False` | If `True`, `f(1)` and `f(1.0)` are cached separately. |

## Cache Introspection

Both `@cache` and `@lru_cache` add these methods to the decorated function:

```python
fibonacci.cache_info()   # CacheInfo(hits=28, misses=31, maxsize=None, currsize=31)
fibonacci.cache_clear()  # empty the cache
```

## When to Use Which

| Scenario | Recommendation |
|---|---|
| Short-lived script, small input space | `@cache` |
| Long-running process | `@lru_cache(maxsize=...)` |
| Need to distinguish `f(1)` from `f(1.0)` | `@lru_cache(typed=True)` |
| Remote API calls (avoid repeat fetches) | Either, with appropriate maxsize |

## Stacking with Other Decorators

Order matters. To cache the results of a clocked function:

```python
@functools.cache     # applied second (outer)
@clock               # applied first (inner)
def fibonacci(n):
    ...
```

This is equivalent to `fibonacci = cache(clock(fibonacci))`.

## See Also

- [[implementing-decorators]] -- the decorator pattern that cache and lru_cache use internally
- [[parameterized-decorators]] -- `@lru_cache(maxsize=N)` is itself a parameterized decorator
