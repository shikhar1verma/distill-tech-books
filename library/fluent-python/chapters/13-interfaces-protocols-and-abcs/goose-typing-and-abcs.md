---
title: "Goose Typing and Abstract Base Classes"
chapter: 13
slug: goose-typing-and-abcs
type: mixed
depends_on:
  - typing-map-four-approaches
tags:
  - ABCs
  - abc-module
  - isinstance
  - goose-typing
  - collections-abc
---

# Goose Typing and Abstract Base Classes

**Goose typing** is Alex Martelli's term for a runtime type-checking discipline: use `isinstance(obj, SomeABC)` where the second argument is an abstract base class, not a concrete type.

## Why "Goose Typing"?

Duck typing checks if an object *looks like* a duck (has the right methods). Goose typing checks if an object *is registered as* a waterfowl (is linked to an ABC). The analogy comes from biological taxonomy -- cladistics (ancestry) vs. phenetics (observed traits).

## Core Rules

1. **`isinstance` is fine... as long as the second argument is an ABC.** (Martelli)
2. Never check `type(foo) is bar` -- it breaks inheritance.
3. Avoid `if/elif/isinstance` chains -- use polymorphism instead.
4. `isinstance` against ABCs is OK to enforce API contracts ("you must implement this to call me").

## ABCs in the Standard Library

The `collections.abc` module defines 17 ABCs organized in clusters:

| Cluster | ABCs | Key Abstract Methods |
|---|---|---|
| Fundamentals | `Iterable`, `Container`, `Sized` | `__iter__`, `__contains__`, `__len__` |
| Collections | `Collection` | (combines the three above) |
| Sequences | `Sequence`, `MutableSequence` | `__getitem__`, `__len__`, + mutators |
| Mappings | `Mapping`, `MutableMapping` | `__getitem__`, `__len__`, `__iter__`, + mutators |
| Sets | `Set`, `MutableSet` | `__contains__`, `__iter__`, `__len__`, + mutators |
| Views | `MappingView`, `ItemsView`, `KeysView`, `ValuesView` | (from `.items()`, `.keys()`, `.values()`) |
| Other | `Iterator`, `Callable`, `Hashable` | `__next__`, `__call__`, `__hash__` |

### Gotcha: isinstance with Hashable and Iterable

- `isinstance(obj, Hashable)` returning `True` does **not** guarantee `hash(obj)` works (e.g., a tuple containing unhashable items).
- `isinstance(obj, Iterable)` returning `False` does not mean the object is not iterable (the interpreter may use `__getitem__` fallback).

**Best practice:** Call `hash(obj)` or `iter(obj)` directly to test.

## Subclassing an ABC

When you subclass an ABC:

- You **must** implement all abstract methods, or `TypeError` is raised at instantiation.
- You **inherit** concrete mixin methods for free (e.g., `Sequence` provides `__contains__`, `__iter__`, `__reversed__`, `index`, `count`).
- You can override inherited methods with more efficient implementations.

```python
class FrenchDeck2(collections.abc.MutableSequence):
    # Must implement: __getitem__, __len__, __setitem__, __delitem__, insert
    # Gets for free: __contains__, __iter__, __reversed__, index, count,
    #                append, reverse, extend, pop, remove, __iadd__
```

## When to Use ABCs

- **Framework extension points** where you need enforced contracts
- **Runtime isinstance checks** when you must verify an API contract
- **Mixin methods** when you want free concrete behavior from the ABC

## When NOT to Create Custom ABCs

Alex Martelli warns: "Don't define custom ABCs in production code." ABCs are tools for building frameworks. 99.9% of Python developers should only *use* existing ABCs, not create new ones.

## See Also

- [[typing-map-four-approaches]] -- goose typing in the typing map
- [[defining-and-subclassing-abcs]] -- creating your own ABCs
- [[virtual-subclasses-and-register]] -- registering classes with ABCs
- [[dynamic-protocols-and-duck-typing]] -- the more informal alternative
