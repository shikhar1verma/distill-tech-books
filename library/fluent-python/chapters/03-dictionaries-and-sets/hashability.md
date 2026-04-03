---
title: "What Is Hashable"
chapter: 3
book: fluent-python
type: concept
slug: hashability
tags: [hashable, hash, eq, dict-keys, set-elements, immutability]
depends_on: []
---

# What Is Hashable

## Overview

An object is **hashable** if:

1. It has a `__hash__()` method that returns an integer which **never changes** during its lifetime.
2. It has an `__eq__()` method for comparison.
3. Objects that compare equal **must** have the same hash code.

Dict keys and set elements must be hashable. Values (in dicts) do not need to be.

## Built-in Hashability Rules

| Type | Hashable? | Notes |
|---|---|---|
| `int`, `float`, `str`, `bytes` | Always | Immutable scalar types |
| `frozenset` | Always | All elements must be hashable |
| `tuple` | Sometimes | Only if **every item** is hashable |
| `list`, `dict`, `set` | Never | Mutable containers |

```python
hash((1, 2, (30, 40)))        # OK
hash((1, 2, frozenset([3])))  # OK
hash((1, 2, [30, 40]))        # TypeError: unhashable type: 'list'
```

## User-Defined Types

By default, user-defined objects are hashable: `__hash__` returns `id()`, and `__eq__` compares by identity. If you override `__eq__` to compare by value, you **must** also define `__hash__` consistently:

```python
class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __eq__(self, other):
        return isinstance(other, Point) and (self._x, self._y) == (other._x, other._y)

    def __hash__(self):
        return hash((self._x, self._y))
```

If you define `__eq__` without `__hash__`, Python sets `__hash__` to `None`, making instances unhashable. This is a safety measure: value-equal objects with different hashes would corrupt dict/set lookups.

## Hash Salting

CPython adds a random salt to `str`, `bytes`, and `datetime` hashes for security (PEP 456). This means hash codes can differ across Python processes, but are constant within a single process.

## Practical Implications

- Always use immutable attributes for hash computation.
- If your `__eq__` depends on mutable state, your object should **not** be hashable.
- Delegate to `hash(tuple_of_fields)` for a correct, easy implementation.

## See Also

- [[set-theory-and-operations]] -- set elements must be hashable
- [[defaultdict-and-missing]] -- dict key lookup relies on hashing
- [[immutable-mappings-and-views]] -- read-only mappings
