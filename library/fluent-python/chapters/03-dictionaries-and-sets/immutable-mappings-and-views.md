---
title: "Immutable Mappings and Dictionary Views"
chapter: 3
book: fluent-python
type: concept
slug: immutable-mappings-and-views
tags: [MappingProxyType, views, dict_keys, dict_items, immutable, read-only]
depends_on:
  - hashability
---

# Immutable Mappings and Dictionary Views

## Overview

Python has no built-in immutable dict, but `types.MappingProxyType` provides a read-only wrapper. Dictionary views (`.keys()`, `.values()`, `.items()`) are lightweight, non-copying projections that support set operations.

## `MappingProxyType` -- Read-Only Proxy

`types.MappingProxyType(d)` returns a **dynamic, read-only** proxy for dict `d`:

```python
from types import MappingProxyType

d = {1: 'A'}
d_proxy = MappingProxyType(d)

d_proxy[1]      # 'A' -- reads work
d_proxy[2] = 'X'  # TypeError -- writes blocked

d[2] = 'B'
d_proxy[2]      # 'B' -- dynamic: changes to d are visible
```

**Use case:** Expose hardware pin mappings, configuration, or other data that should not be modified by callers. Store the real dict privately; expose only the proxy.

## Dictionary Views

The methods `.keys()`, `.values()`, and `.items()` return **view objects**, not lists (unlike Python 2). Views are:

- **Lightweight:** no data copying; they reference the dict's internal structures.
- **Dynamic:** changes to the dict are immediately visible through existing views.
- **Not subscriptable:** you cannot do `view[0]`. Convert to `list()` if you need indexing.

```python
d = dict(a=10, b=20, c=30)
values = d.values()
d['z'] = 99
list(values)  # [10, 20, 30, 99] -- dynamic!
```

All views support `len()`, iteration, `in`, and `reversed()`.

## Set Operations on Views

`dict_keys` and `dict_items` implement set-like operations:

| Operation | Syntax | Result |
|---|---|---|
| Intersection | `d1.keys() & d2.keys()` | `set` |
| Union | `d1.keys() \| d2.keys()` | `set` |
| Difference | `d1.keys() - d2.keys()` | `set` |
| Symmetric diff | `d1.keys() ^ d2.keys()` | `set` |

These also work with regular `set` operands:

```python
d = dict(a=1, b=2, c=3)
vowels = {'a', 'e', 'i'}
d.keys() & vowels   # {'a'}
d.keys() | vowels   # {'a', 'b', 'c', 'e', 'i'}
```

**Note:** `dict_items` views only support set operations if all values in the dict are hashable.

`dict_values` does NOT support set operations (values are not guaranteed unique or hashable).

## Practical Consequences of How dict Works

- Keys must be hashable (see [[hashability]]).
- Key lookup is O(1) average via hash table.
- Key insertion order is preserved (guaranteed since Python 3.7).
- Dicts have memory overhead due to hash tables (at least 1/3 of rows kept empty).
- Define all instance attributes in `__init__` to benefit from key-sharing dicts (PEP 412).

## See Also

- [[hashability]] -- required for dict keys and set elements
- [[set-theory-and-operations]] -- full set operations
- [[dict-variations]] -- specialized mapping types
