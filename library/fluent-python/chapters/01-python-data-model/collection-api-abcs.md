---
title: "Collection API and ABCs"
book: "Fluent Python"
chapter: 1
tags: [python, data-model, abc, collections, sequence, mapping, set, iterable, sized, container]
related:
  - "[[special-dunder-methods]]"
  - "[[sequence-protocol-french-deck]]"
  - "[[boolean-value-custom-types]]"
---

## Summary

The `collections.abc` module defines abstract base classes (ABCs) that formalize the interfaces of Python's core collection types. The three fundamental ABCs -- `Iterable`, `Sized`, and `Container` -- are unified by `Collection` (added in Python 3.6). Specialized ABCs like `Sequence`, `Mapping`, and `Set` extend `Collection` with additional methods. Importantly, Python does not require your classes to inherit from these ABCs; implementing the right special methods is enough (duck typing / structural subtyping).

## How It Works

### The ABC Hierarchy

The collection ABCs form a hierarchy where each level adds requirements:

**Top-level ABCs** (one special method each):

| ABC | Required method | Supports |
|-----|----------------|----------|
| `Iterable` | `__iter__` | `for` loops, unpacking |
| `Sized` | `__len__` | `len()` built-in |
| `Container` | `__contains__` | `in` operator |

**`Collection`** (Python 3.6+) combines all three:
- Requires: `__iter__`, `__len__`, `__contains__`

**Specialized collections** extend `Collection`:

| ABC | Key additional methods | Built-in examples |
|-----|----------------------|-------------------|
| `Sequence` | `__getitem__`, `__reversed__`, `index`, `count` | `list`, `str`, `tuple` |
| `Mapping` | `__getitem__`, `keys`, `items`, `values`, `get` | `dict`, `defaultdict` |
| `Set` | `__le__`, `__and__`, `__or__`, `__xor__`, `isdisjoint` | `set`, `frozenset` |

Only `Sequence` is `Reversible`, because sequences maintain a meaningful order that can be reversed, while mappings and sets do not.

### Abstract vs Concrete Methods

Each ABC defines both **abstract** methods (which you must implement) and **concrete** methods (which you get for free). For example, `Sequence` requires only `__getitem__` and `__len__` as abstract methods, but provides concrete implementations of `__contains__`, `__iter__`, `__reversed__`, `index`, and `count`:

```python
from collections.abc import Sequence

class MySeq(Sequence):
    def __init__(self, data):
        self._data = list(data)

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        return len(self._data)

# __contains__, __iter__, __reversed__, index, count
# are all provided by the Sequence ABC
s = MySeq([10, 20, 30])
print(20 in s)          # True (via inherited __contains__)
print(s.index(30))      # 2 (via inherited index)
print(s.count(20))      # 1 (via inherited count)
```

### Structural Subtyping (Duck Typing)

Python does not require inheritance to satisfy an ABC. Any class with `__len__` is considered a `Sized` subclass by `isinstance`:

```python
from collections.abc import Sized

class Bag:
    def __len__(self):
        return 42

isinstance(Bag(), Sized)  # True -- no inheritance needed!
```

This works through a mechanism called **virtual subclassing**. The `Sized` ABC defines a `__subclasshook__` that checks for the presence of `__len__`, regardless of inheritance.

However, not all ABCs use `__subclasshook__`. For example, `Sequence` does not -- you must either inherit from it or explicitly register:

```python
from collections.abc import Sequence

class FrenchDeck:
    def __getitem__(self, pos): ...
    def __len__(self): ...

isinstance(FrenchDeck(), Sequence)  # False -- Sequence has no __subclasshook__
```

### `dict` Ordering Since Python 3.7

Since Python 3.7, `dict` preserves key insertion order. However, `dict` is a `Mapping`, not a `Sequence`. You cannot use integer indexing on a dict, and you cannot rearrange keys arbitrarily. The ordering is a side effect of the implementation, not a sequence contract.

## In Practice

### When to Use ABCs

**Type checking and `isinstance`:** ABCs are useful for type checking in function signatures or runtime checks:

```python
from collections.abc import Mapping, Sequence

def process(data):
    if isinstance(data, Mapping):
        # handle dict-like objects
        for key, value in data.items():
            ...
    elif isinstance(data, Sequence):
        # handle list-like objects
        for item in data:
            ...
```

**Enforcing interfaces:** If you want to ensure subclasses implement required methods, inherit from the ABC. Attempting to instantiate a class that does not implement all abstract methods raises `TypeError`:

```python
from collections.abc import Sequence

class BadSeq(Sequence):
    pass

# BadSeq()  # TypeError: Can't instantiate abstract class BadSeq
#              with abstract methods __getitem__, __len__
```

**Type annotations (typing module):** The `typing` module provides generic versions of these ABCs for static type checking:

```python
from typing import Sequence, Mapping

def first(items: Sequence[int]) -> int:
    return items[0]
```

### When Not to Use ABCs

For most application code, you do not need to inherit from ABCs or check `isinstance`. Duck typing works well: if an object has `__getitem__` and `__len__`, it works as a sequence in practice, even without any formal relationship to `Sequence`.

ABCs are most valuable in **library and framework code** where you need to handle multiple collection types generically.

## Common Pitfalls

1. **Confusing ABC `isinstance` checks with actual capability.** `isinstance(deck, Iterable)` is `False` for a class with only `__getitem__` (no `__iter__`), even though `for item in deck` works. The `__getitem__` fallback for iteration is a Python feature that ABCs do not account for.

2. **Over-inheriting.** Inheriting from `Sequence` or `MutableSequence` commits you to their full interface. If you only need a subset of sequence behavior, prefer composition (like FrenchDeck) over inheritance.

3. **Assuming `Mapping` is `Reversible`.** Since Python 3.8, `dict` supports `reversed()`, and `Mapping` gained a `__reversed__` method, but this was a late addition. Older custom mappings may not support it.

4. **Forgetting `Set` operators are special methods.** All operators on `Set` (`&`, `|`, `^`, `<`, `<=`) are implemented via special methods (`__and__`, `__or__`, etc.). This means you can use these operators with any `Set` subclass.

5. **Not registering virtual subclasses.** If you want `isinstance` checks to work with your class and an ABC that lacks `__subclasshook__`, you must register explicitly:
   ```python
   Sequence.register(FrenchDeck)
   isinstance(FrenchDeck(), Sequence)  # now True
   ```

## See Also

- [[special-dunder-methods]] -- The special methods that ABCs formalize
- [[sequence-protocol-french-deck]] -- A practical Sequence implementation without ABC inheritance
- [[boolean-value-custom-types]] -- How `__len__` provides truthiness for collections
