---
title: "Positional-Only and Keyword-Only Parameters"
book: "Fluent Python"
chapter: 7
tags: [parameters, keyword-only, positional-only, function-signatures, python-3.8]
related:
  - "[[first-class-functions]]"
  - "[[replacing-map-filter-reduce]]"
---

# Positional-Only and Keyword-Only Parameters

## Summary

Python provides fine-grained control over how callers pass arguments to functions. **Keyword-only parameters** (Python 3.0+) appear after `*` or `*args` in the signature and must be passed by name. **Positional-only parameters** (Python 3.8+) appear before `/` in the signature and cannot be passed by keyword. Together with `*args` and `**kwargs`, these markers let API designers express exactly how their functions should be called.

## How It Works

### The full parameter spectrum

```
def f(pos_only, /, normal, *, kw_only):
    ...
```

| Region | Syntax | How caller passes |
|--------|--------|------------------|
| Before `/` | positional-only | `f(1, ...)` -- keyword forbidden |
| Between `/` and `*` | normal | `f(1, 2, ...)` or `f(1, normal=2, ...)` |
| After `*` | keyword-only | `f(..., kw_only=3)` -- positional forbidden |

### Keyword-only parameters

```python
def f(a, *, b):
    return a, b

f(1, b=2)      # OK: (1, 2)
f(1, 2)        # TypeError: f() takes 1 positional argument but 2 were given
```

In a function with `*args`, everything after `*args` is keyword-only:

```python
def tag(name, *content, class_=None, **attrs):
    ...

# class_ can ONLY be passed as a keyword argument
tag("p", "hello", class_="sidebar")
```

### Positional-only parameters (Python 3.8+)

```python
def divmod(a, b, /):
    return (a // b, a % b)

divmod(10, 3)          # OK: (3, 1)
divmod(a=10, b=3)      # TypeError
```

### Combining both

```python
def tag(name, /, *content, class_=None, **attrs):
    """name is positional-only; class_ is keyword-only."""
    ...

tag("p", "hello", class_="main")   # OK
tag(name="p", "hello")             # TypeError — name is positional-only
```

## In Practice

- **Positional-only for names that are implementation details:** `def connect(host, port, /)` prevents callers from depending on parameter names, making future refactoring safe.
- **Keyword-only for flags and options:** `def fetch(url, *, timeout=30, retries=3)` forces callers to be explicit about optional behavior.
- **`*` alone in the signature:** Use `def f(a, *, b)` when you do not want `*args` but still want keyword-only parameters.
- **The `tag()` pattern:** `def tag(name, /, *content, class_=None, **attrs)` is an excellent real-world example showing all parameter types together.

## Common Pitfalls

- **`/` syntax requires Python 3.8+:** Code using positional-only parameters will raise `SyntaxError` on Python 3.7 and earlier.
- **Keyword-only does not mean optional:** `def f(*, b)` makes `b` keyword-only *and* mandatory. Add a default value to make it optional.
- **`**kwargs` swallows everything:** Misspelled keyword arguments silently land in `**kwargs` instead of raising `TypeError`. Validate kwargs or avoid `**kwargs` when possible.
- **Confusing `*args` with `*`:** `def f(*args, b)` captures variable positional args; `def f(*, b)` takes no variable positional args but still makes `b` keyword-only.

## See Also

- [[first-class-functions]] -- Functions as first-class objects
- [[replacing-map-filter-reduce]] -- `functools.partial` binds positional and keyword arguments
- PEP 3102 -- Keyword-Only Arguments
- PEP 570 -- Python Positional-Only Parameters
