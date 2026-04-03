---
title: "defaultdict and __missing__"
chapter: 3
book: fluent-python
type: concept
slug: defaultdict-and-missing
tags: [defaultdict, missing, setdefault, dict, collections]
depends_on:
  - hashability
---

# defaultdict and `__missing__`

## Overview

Python provides several mechanisms for handling missing dict keys gracefully:

1. **`dict.get(key, default)`** -- returns a default without modifying the dict.
2. **`dict.setdefault(key, default)`** -- returns existing value or inserts and returns the default in a single lookup.
3. **`collections.defaultdict`** -- auto-creates missing values via a callable factory.
4. **`__missing__`** -- a special method called by `dict.__getitem__` when a key is not found.

## `setdefault` -- Avoid Redundant Lookups

```python
# Without setdefault: 2-3 lookups
occurrences = index.get(word, [])
occurrences.append(location)
index[word] = occurrences

# With setdefault: 1 lookup
index.setdefault(word, []).append(location)
```

`setdefault` returns the existing value if the key is present, or inserts the default and returns it, all in one operation.

## `defaultdict` -- Factory-Based Defaults

Provide a callable (`list`, `int`, `set`, `lambda: ...`) at construction time. When `d[key]` misses, the `default_factory` is called to produce a value, which is inserted and returned:

```python
from collections import defaultdict
index = defaultdict(list)
index['word'].append((1, 5))  # No KeyError -- list() called automatically
```

**Important:** `default_factory` is only triggered by `__getitem__` (`d[key]`). It is NOT triggered by `d.get(key)` or `key in d`.

## `__missing__` -- Custom Missing-Key Logic

If you subclass `dict` and define `__missing__`, it is called by `dict.__getitem__` whenever a key is not found:

```python
class StrKeyDict(dict):
    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)   # prevent infinite recursion
        return self[str(key)]     # retry with str(key)
```

The `isinstance` guard is critical: without it, `self[str(key)]` could call `__missing__` again endlessly if the string version of the key is also missing.

## Inconsistent `__missing__` Behavior

The standard library is inconsistent about when `__missing__` is invoked:

| Base class | `d[key]` | `d.get(key)` | `key in d` |
|---|---|---|---|
| `dict` subclass | calls `__missing__` | does NOT | does NOT |
| `UserDict` subclass | calls `__missing__` | calls `__missing__` (via `__getitem__`) | does NOT |

This is one reason to prefer `UserDict` as a base class for custom mappings.

## When to Use Which

| Situation | Tool |
|---|---|
| Simple one-off default | `d.get(key, default)` |
| Insert-if-missing pattern | `d.setdefault(key, default)` |
| All missing keys get same type | `defaultdict(factory)` |
| Custom fallback logic | `__missing__` in a `dict` / `UserDict` subclass |

## See Also

- [[dict-variations]] -- UserDict and other specialized mappings
- [[hashability]] -- keys must be hashable for any of these to work
