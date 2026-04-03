---
title: "Mixin Classes"
book: "Fluent Python"
chapter: 14
tags: [python, oop, mixins, multiple-inheritance, code-reuse]
related:
  - "[[super-function]]"
  - "[[multiple-inheritance-mro]]"
  - "[[cooperative-multiple-inheritance]]"
  - "[[cooperative-multiple-inheritance]]"
---

# Mixin Classes

> **One-sentence summary.** A mixin is a class designed to provide specific method implementations for reuse via multiple inheritance, without defining a standalone type; by convention it is named with a `Mixin` suffix and always delegates to siblings via `super()`.

## How It Works

A mixin class bundles a small set of closely related methods that add or customize behavior. It is never meant to be instantiated on its own or to serve as the sole base class of a concrete class. Instead, it is combined with other classes in a multiple inheritance declaration.

Key characteristics of a well-designed mixin:
- Provides a **single, focused behavior** (e.g., case-insensitive key handling)
- All methods call `super()` to cooperate with sibling classes in the MRO
- Has **no instance state** of its own (no `__init__` setting attributes, ideally)
- Is named with a `Mixin` suffix to signal intent

```python
import collections

def _upper(key):
    try:
        return key.upper()
    except AttributeError:
        return key

class UpperCaseMixin:
    """Mixin that uppercases string keys in a mapping."""

    def __setitem__(self, key, item):
        super().__setitem__(_upper(key), item)

    def __getitem__(self, key):
        return super().__getitem__(_upper(key))

    def get(self, key, default=None):
        return super().get(_upper(key), default)

    def __contains__(self, key):
        return super().__contains__(_upper(key))
```

The mixin is useless by itself — it calls `super()` for every operation, expecting a real mapping implementation further down the MRO. You combine it with a concrete mapping class:

```python
class UpperDict(UpperCaseMixin, collections.UserDict):
    pass

d = UpperDict([('a', 'letter A'), (2, 'digit two')])
print(list(d.keys()))  # ['A', 2]
print('b' in d)        # after d['b'] = ... → True (uppercased to 'B')
```

### Mixin ordering matters

The mixin must appear **before** the concrete class in the base list so that its methods are found first in the MRO. `class UpperDict(UpperCaseMixin, UserDict)` is correct; `class UpperDict(UserDict, UpperCaseMixin)` would skip the mixin entirely.

## In Practice

**Standard library examples**: `socketserver.ThreadingMixIn` adds threaded request handling to any server class. The entire `ThreadingHTTPServer` is just:

```python
class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True
```

**collections.abc as mixins**: ABCs like `MutableMapping` provide mixin methods (`update`, `pop`, `setdefault`) that work once you implement the abstract methods (`__getitem__`, `__setitem__`, `__delitem__`, `__len__`, `__iter__`).

**Reusing the same mixin with different bases**: `UpperCaseMixin` works with both `UserDict` and `Counter` — the mixin doesn't care what concrete class provides the mapping implementation.

## Common Pitfalls

- **Forgetting `super()` in the mixin**: If a mixin method doesn't call `super()`, it blocks the chain and the concrete class's method never runs.
- **Mixin ordering**: Placing the mixin after the concrete class in the base list means it is never reached in the MRO.
- **Stateful mixins**: Adding instance attributes to a mixin complicates `__init__` cooperation. If you must, use `**kwargs` forwarding and always call `super().__init__(**kwargs)`.
- **Not naming it with Mixin suffix**: Python has no formal mixin construct. The naming convention is the only signal to other developers.

## See Also

- [[super-function]] — the mechanism that makes mixin delegation work
- [[multiple-inheritance-mro]] — why mixin ordering in the base list matters
- [[cooperative-multiple-inheritance]] — the contract that all mixin methods must follow
- [[cooperative-multiple-inheritance]] — guidelines for designing and naming mixins
