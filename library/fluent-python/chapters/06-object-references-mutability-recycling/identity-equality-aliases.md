---
title: "Identity, Equality, and Aliases"
slug: identity-equality-aliases
chapter: 6
book: fluent-python
type: mixed
depends_on:
  - variables-are-labels
tags: [identity, equality, is, ==, aliases, id, __eq__, None, sentinel]
---

# Identity, Equality, and Aliases

## Two Ways to Compare Objects

Every Python object has three properties: **identity** (unique ID, never changes), **type**, and **value** (may change for mutable objects).

| Operator | What it tests | Mechanism |
|----------|--------------|-----------|
| `==` | **Equality** -- same value? | Calls `a.__eq__(b)` |
| `is` | **Identity** -- same object? | Compares `id(a) == id(b)` |

```python
charles = {"name": "Charles L. Dodgson", "born": 1832}
lewis = charles          # alias -- same object

lewis is charles         # True  (same identity)
lewis == charles         # True  (same value, trivially)

alex = {"name": "Charles L. Dodgson", "born": 1832}
alex == charles          # True  (same value)
alex is charles          # False (different objects)
```

## Aliases

When two or more variables are bound to the **same** object, they are called **aliases**. Any mutation via one alias is visible through all others.

```python
lewis["balance"] = 950
charles["balance"]       # 950 -- same object
```

## When to Use `is`

Use `is` (and `is not`) only for **singletons**:

```python
# The canonical use-case
if x is None:
    ...

if x is not None:
    ...

# Sentinel objects
END = object()
if value is END:
    ...
```

For everything else, use `==`. The `is` operator is faster (it just compares two integers), but `==` is what you almost always *mean*.

### Common Mistake

```python
# WRONG -- do not use 'is' to compare strings or numbers
if name is "Alice":    # may work due to interning, but unreliable
    ...

# CORRECT
if name == "Alice":
    ...
```

## How `==` Works Under the Hood

`a == b` is syntactic sugar for `a.__eq__(b)`. The default `__eq__` inherited from `object` compares identity (same as `is`). Most built-in types override it to compare values:

- `list.__eq__` compares elements pairwise.
- `dict.__eq__` compares all key-value pairs.
- `str.__eq__` compares character sequences.

If you define a custom class without `__eq__`, instances are only equal to themselves.

## The `id()` Function

`id()` returns an integer guaranteed to be unique for the object's lifetime. In CPython this is the memory address. You rarely need `id()` in production code, but it is useful when debugging to verify whether two references are aliases.

## Key Takeaway

> `==` asks "do these have the same value?" -- use this by default. `is` asks "are these the same object in memory?" -- use this only for `None` and sentinels.
