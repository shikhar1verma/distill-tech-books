---
title: "Caching Properties: cached_property, @property + @cache"
book: "Fluent Python"
chapter: 22
tags: [python, cached-property, functools, performance, descriptors]
related:
  - "[[computed-properties]]"
  - "[[property-for-validation]]"
  - "[[overriding-vs-nonoverriding-descriptors]]"
---

# Caching Properties: `cached_property`, `@property` + `@cache`

> **Computed properties can be expensive. Python's `functools` module provides two decorator-based caching strategies, each with different trade-offs regarding descriptor type, name clashes, and memory optimization.**

## Why Cache Properties?

Users expect `event.venue` to be cheap -- it looks like reading a plain attribute. But if the property computes a value by querying a database, fetching from a network, or traversing a data structure, repeating that work on every access is wasteful. Caching the result after the first computation is a common need.

## Approach 1: `functools.cached_property` (Python 3.8+)

The simplest and most Pythonic option for new computed attributes:

```python
from functools import cached_property

class Event(Record):
    @cached_property
    def venue(self):
        key = f'venue.{self.venue_serial}'
        return self.__class__.fetch(key)
```

After the first access, `cached_property` stores the computed value as a **same-named instance attribute**. Subsequent reads find the instance attribute directly in `__dict__` and never call the method again.

**How it works internally:** `cached_property` is a **non-overriding descriptor** (it defines `__get__` but not `__set__`). On first access, `__get__` runs the decorated function, writes the result into `instance.__dict__`, and returns it. On subsequent accesses, Python finds the instance attribute in `__dict__` before consulting the descriptor, so the method is never called again.

**Clearing the cache:** Simply `del obj.venue`. The next access re-triggers the computation.

**Thread safety:** `cached_property` uses a reentrant lock internally, making it safe for multithreaded programs.

### Limitations

1. **Cannot replace `@property` when the method depends on an instance attribute with the same name.** For example, a `speakers` property that needs to read a `speakers` list stored as instance data. Since `cached_property` is non-overriding, the existing `speakers` instance attribute would always shadow it, preventing the method from ever running.

2. **Cannot be used with `__slots__`.** It needs to write to `instance.__dict__`, which does not exist in `__slots__`-only classes.

3. **Defeats PEP 412 key-sharing optimization.** It creates instance attributes after `__init__`, which forces Python to allocate a separate dict key hash table for the instance instead of sharing one with other instances of the same class.

## Approach 2: `@property` + `@functools.cache`

When `cached_property` cannot be used (typically due to a name clash), stack `@property` on top of `@cache`:

```python
from functools import cache

class Event(Record):
    @property
    @cache
    def speakers(self):
        spkr_serials = self.__dict__['speakers']
        fetch = self.__class__.fetch
        return [fetch(f'speaker.{key}') for key in spkr_serials]
```

**Decorator order matters.** Reading bottom-up: `@cache` wraps the `speakers` function first (adding memoization), then `@property` wraps the cached version (making it a descriptor). This is equivalent to `speakers = property(cache(speakers))`.

Since `@property` creates an **overriding descriptor**, it takes precedence over the `speakers` instance attribute, ensuring the property method is always called. The `@cache` layer then returns the memoized result after the first invocation.

## Approach 3: Hand-Rolled Cache (Legacy)

Before `cached_property` existed, developers wrote their own caching logic:

```python
@property
def speakers(self):
    if not hasattr(self, '__speaker_objs'):
        spkr_serials = self.__dict__['speakers']
        fetch = self.__class__.fetch
        self.__speaker_objs = [fetch(f'speaker.{key}') for key in spkr_serials]
    return self.__speaker_objs
```

This works but has two problems:

1. **Defeats PEP 412 key-sharing.** Creating `__speaker_objs` after `__init__` means the instance dict can no longer share its key hash table with other instances.

2. **Race conditions in multithreaded code.** Two threads could simultaneously see that `__speaker_objs` does not exist yet, both start computing it, and one might read an incomplete result written by the other.

A PEP 412-friendly alternative initializes the cache slot in `__init__`:

```python
class Event(Record):
    def __init__(self, **kwargs):
        self.__speaker_objs = None
        super().__init__(**kwargs)

    @property
    def speakers(self):
        if self.__speaker_objs is None:
            spkr_serials = self.__dict__['speakers']
            fetch = self.__class__.fetch
            self.__speaker_objs = [fetch(f'speaker.{key}') for key in spkr_serials]
        return self.__speaker_objs
```

This preserves key-sharing because all instances create the same set of keys during `__init__`, but it is verbose and still not thread-safe.

## Choosing the Right Approach

| Criterion | `cached_property` | `@property + @cache` | Hand-rolled |
|---|---|---|---|
| Simplicity | Best | Good | Verbose |
| Thread safety | Yes (reentrant lock) | Yes (`cache` is thread-safe) | No (without explicit locking) |
| Name clash with instance attr | Cannot handle | Works | Works |
| `__slots__` compatibility | No | Yes | Depends |
| PEP 412 key-sharing | Defeats it | Preserves it | Defeats it (unless `__init__` pre-creates) |

## Connections

- The distinction between overriding and non-overriding descriptors explains why `cached_property` and `property` behave differently (see [[overriding-vs-nonoverriding-descriptors]]).
- Read-only computed properties are introduced in [[computed-properties]].
- Validation properties that need read/write access are in [[property-for-validation]].
