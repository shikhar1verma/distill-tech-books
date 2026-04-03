---
title: "The Nine Flavors of Callable Objects"
book: "Fluent Python"
chapter: 7
tags: [callable, call-operator, callable-types, python-data-model]
related:
  - "[[first-class-functions]]"
  - "[[user-defined-callable-types]]"
  - "[[special-dunder-methods]]"
---

# The Nine Flavors of Callable Objects

## Summary

The call operator `()` can be applied to many kinds of objects in Python, not just functions. As of Python 3.9, there are **nine callable types**. Use the `callable()` built-in to check whether any object is callable.

## How It Works

### The nine callable types

| # | Type | Created by | Notes |
|---|------|-----------|-------|
| 1 | **User-defined functions** | `def` or `lambda` | The most common callable |
| 2 | **Built-in functions** | Implemented in C | `len`, `abs`, `time.strftime` |
| 3 | **Built-in methods** | Implemented in C | `dict.get`, `list.append` |
| 4 | **Methods** | `def` inside a class body | Bound to an instance or class |
| 5 | **Classes** | `class` statement | Calling triggers `__new__` + `__init__` |
| 6 | **Class instances** | Classes with `__call__` | Function-like objects with state |
| 7 | **Generator functions** | `def` with `yield` | Return a generator iterator |
| 8 | **Native coroutine functions** | `async def` (3.5+) | Return a coroutine object |
| 9 | **Async generator functions** | `async def` + `yield` (3.6+) | Return an async generator |

### Testing with `callable()`

```python
>>> callable(abs)        # True  — built-in function
>>> callable(str)        # True  — class
>>> callable("hello")    # False — string instance
>>> callable(13)         # False — integer instance

>>> [callable(obj) for obj in (abs, str, "Ni!")]
[True, True, False]
```

### Important distinction

Types 7-9 (generators, coroutines, async generators) are callable, but their return values are **not application data**. They return iterator/coroutine objects that require further processing (iteration, `await`, `async for`).

## In Practice

- **`callable()` for duck typing:** Before calling an unknown object, check `callable(obj)` rather than checking its type.
- **Classes are callable:** Python has no `new` keyword. `MyClass()` is simply calling the class object, which triggers `__new__` and `__init__`.
- **Registries and dispatch:** You can store any callable type in a dict for dispatch -- functions, classes, and `__call__`-implementing instances all work interchangeably.

## Common Pitfalls

- **Assuming only functions are callable:** Classes, methods, and instances with `__call__` are also callable. Always use `callable()` to test.
- **Calling a non-callable:** Produces `TypeError: 'X' object is not callable`. Common when you accidentally overwrite a function name with a value (e.g., `list = [1,2,3]` then `list(...)` fails).
- **Generator functions vs. generators:** Calling a generator function does not run its body; it returns a generator object. You must iterate to get values.

## See Also

- [[first-class-functions]] -- Functions as first-class objects
- [[user-defined-callable-types]] -- Making class instances callable with `__call__`
- [[special-dunder-methods]] -- The `__call__` protocol in the data model
- Chapter 17 covers generators; Chapter 21 covers coroutines and async generators
