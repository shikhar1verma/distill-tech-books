---
title: "Dict Variations: OrderedDict, ChainMap, Counter, UserDict"
chapter: 3
book: fluent-python
type: concept
slug: dict-variations
tags: [OrderedDict, ChainMap, Counter, UserDict, collections]
depends_on:
  - defaultdict-and-missing
---

# Dict Variations: OrderedDict, ChainMap, Counter, UserDict

## Overview

The `collections` module provides several specialized mapping types that extend the basic `dict` with additional behavior.

## `collections.OrderedDict`

Since Python 3.7, plain `dict` preserves insertion order. However, `OrderedDict` still has unique features:

- **Equality considers order:** `OrderedDict(a=1, b=2) != OrderedDict(b=2, a=1)`, whereas plain dicts would be equal.
- **`move_to_end(key, last=True)`:** efficiently repositions a key to either end.
- **`popitem(last=True)`:** accepts a `last` parameter to pop from either end (plain `dict.popitem()` always pops the last item).

Best for: LRU caches, order-sensitive comparisons, backward compatibility.

## `collections.ChainMap`

Holds a list of mappings and searches them in order. The first match wins. Writes go to the **first** mapping only.

```python
from collections import ChainMap
defaults = {'color': 'blue', 'size': 'M'}
user = {'color': 'red'}
config = ChainMap(user, defaults)
config['color']  # 'red' (user wins)
config['size']   # 'M'   (from defaults)
```

ChainMap holds **references**, not copies. Changes to the underlying dicts are reflected. Useful for implementing variable scoping (like Python's own local/global/builtin lookup).

## `collections.Counter`

A dict subclass where values are integer counts. Acts as a **multiset** (bag).

```python
from collections import Counter
ct = Counter('abracadabra')
ct.most_common(3)  # [('a', 5), ('b', 2), ('r', 2)]
```

Supports arithmetic: `+` combines tallies, `-` subtracts (dropping non-positive), `&` gives minimum counts, `|` gives maximum counts.

## `collections.UserDict`

An intentionally simple wrapper around a `dict` stored in the `.data` attribute. Designed as the **proper base class for custom mappings**.

### Why Not Subclass `dict` Directly?

`dict` has C-level shortcuts that can bypass your overridden methods. For example, `dict.update` may not call your `__setitem__`. `UserDict` avoids this because:

1. It uses **composition** (an inner `self.data` dict), not inheritance from the C `dict`.
2. All standard methods route through your overrides consistently.
3. `__contains__` can safely check `self.data` without recursion risks.

```python
import collections

class StrKeyDict(collections.UserDict):
    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)
        return self[str(key)]

    def __contains__(self, key):
        return str(key) in self.data

    def __setitem__(self, key, item):
        self.data[str(key)] = item
```

## `shelve.Shelf`

A persistent mapping backed by `dbm` with `pickle` serialization. Keys must be strings; values must be picklable. Acts as a context manager. Useful for simple key-value persistence without a full database.

## Quick Comparison

| Type | Key feature | Mutable? |
|---|---|---|
| `dict` | General-purpose, fast | Yes |
| `OrderedDict` | Order-aware `==`, `move_to_end` | Yes |
| `ChainMap` | Layered lookup, writes to first map | Yes |
| `Counter` | Integer tallies, multiset ops | Yes |
| `UserDict` | Safe base for subclassing | Yes |
| `shelve.Shelf` | Persistent on disk | Yes |

## See Also

- [[defaultdict-and-missing]] -- another collections mapping
- [[immutable-mappings-and-views]] -- read-only wrappers
- [[dict-comprehensions-unpacking-merging]] -- building dicts
