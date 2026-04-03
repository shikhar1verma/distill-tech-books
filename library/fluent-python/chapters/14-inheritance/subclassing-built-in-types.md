---
title: "Subclassing Built-In Types Is Tricky"
book: "Fluent Python"
chapter: 14
tags: [python, oop, inheritance, builtins]
related:
  - "[[super-function]]"
  - "[[cooperative-multiple-inheritance]]"
---

# Subclassing Built-In Types Is Tricky

> **One-sentence summary.** Built-in types like `dict`, `list`, and `str` are implemented in C, and their internal methods do not call overridden methods in Python subclasses — use `UserDict`, `UserList`, and `UserString` from `collections` instead.

## How It Works

Since Python 2.2 you can subclass built-in types, but there is a major caveat: the C-level implementation of built-ins takes shortcuts that bypass your Python-level method overrides. For example, `dict.__init__` and `dict.update` do **not** call `__setitem__` when populating the dictionary, even if you override `__setitem__` in a subclass.

```python
class DoppelDict(dict):
    """Doubles every value on storage."""
    def __setitem__(self, key, value):
        super().__setitem__(key, [value] * 2)

dd = DoppelDict(one=1)
print(dd)            # {'one': 1} — NOT doubled! __init__ ignored our override

dd['two'] = 2
print(dd['two'])     # [2, 2] — direct [] calls our __setitem__

dd.update(three=3)
print(dd['three'])   # 3 — NOT doubled! update ignored our override
```

This violates the principle of late binding: in proper OOP, `x.method()` should always resolve based on the runtime class of `x`. The CPython built-ins behave more like C++ non-virtual methods.

### The fix: collections.UserDict, UserList, UserString

These wrapper classes are written in pure Python. They delegate to an internal built-in instance but properly call your overridden methods:

```python
import collections

class DoppelDict2(collections.UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, [value] * 2)

dd2 = DoppelDict2(one=1)
print(dd2)  # {'one': [1, 1]} — correctly doubled everywhere!
```

## In Practice

Any time you need a custom `dict`, `list`, or `str`, reach for the `User*` variants from `collections`:

- **Custom dict with default behavior** — subclass `UserDict`, override `__missing__`, `__setitem__`, etc.
- **Custom list with validation** — subclass `UserList`, override `append`, `__setitem__`, etc.
- **Custom string with extra methods** — subclass `UserString`

If the behavior you want is very different from the built-in, consider subclassing the appropriate ABC from `collections.abc` (like `MutableMapping`) and writing your own implementation from scratch.

## Common Pitfalls

- **Assuming your overrides will be called**: The most common trap. You override `__getitem__` on a `dict` subclass, then wonder why `dict.update()` ignores it.
- **Extra work to compensate**: If you insist on subclassing `dict` directly, you may need to override `__init__`, `get`, `update`, and other methods — effectively doubling your code compared to `UserDict`.
- **PyPy behaves differently**: PyPy's built-in types *do* call overridden methods, making code that works on PyPy fail on CPython (or vice versa).

## See Also

- [[super-function]] — the correct way to delegate to parent methods
- [[cooperative-multiple-inheritance]] — "avoid subclassing concrete classes" directly addresses this issue
