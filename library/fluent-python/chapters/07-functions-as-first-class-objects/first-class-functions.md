---
title: "First-Class Functions"
book: "Fluent Python"
chapter: 7
tags: [first-class-objects, functions, python-fundamentals]
related:
  - "[[higher-order-functions]]"
  - "[[callable-types]]"
  - "[[anonymous-functions-lambda]]"
  - "[[classic-strategy-pattern]]"
---

# First-Class Functions

## Summary

In Python, functions are **first-class objects** -- they satisfy the same criteria as integers, strings, and other objects. A first-class object can be created at runtime, assigned to a variable, stored in a data structure, passed as an argument, and returned as the result of a function. This is the foundation of functional programming patterns in Python and the key enabler for higher-order functions, decorators, callbacks, and the strategy pattern.

## How It Works

A function created with `def` or `lambda` is an instance of the `function` class. Like any other object, it has attributes (`__doc__`, `__name__`, `__defaults__`, etc.) and can be manipulated freely.

```python
def factorial(n):
    """returns n!"""
    return 1 if n < 2 else n * factorial(n - 1)

# Inspect the object
print(type(factorial))      # <class 'function'>
print(factorial.__doc__)    # 'returns n!'
print(factorial.__name__)   # 'factorial'

# Assign to another variable
fact = factorial
print(fact(5))              # 120

# Pass as an argument
print(list(map(factorial, range(6))))  # [1, 1, 2, 6, 24, 120]

# Store in a data structure
ops = {"!": factorial, "hex": hex}
print(ops["!"](4))         # 24
```

## In Practice

- **Callbacks and event handlers:** Pass functions to frameworks that call them later (e.g., GUI button handlers, web route decorators).
- **Strategy pattern:** Instead of creating a class hierarchy for each strategy, pass a plain function.
- **Sorting keys:** `sorted(data, key=some_function)` is idiomatic Python.
- **Function registries:** Store functions in dicts or lists for dispatch tables.

## Common Pitfalls

- **Forgetting parentheses:** `f = factorial` assigns the function object; `f = factorial()` calls it with zero args (and raises `TypeError` for factorial).
- **Mutable default arguments:** Default values are evaluated once at function definition time. Never use mutable defaults like `def f(items=[])`.
- **Confusing identity and equality:** `fact is factorial` is `True` (same object), but two different functions that do the same thing are not equal.

## See Also

- [[higher-order-functions]] -- Functions that accept or return other functions
- [[callable-types]] -- The nine kinds of callable objects in Python
- [[anonymous-functions-lambda]] -- Creating throwaway functions with `lambda`
- Chapter 9 covers closures and decorators, which build on first-class functions
