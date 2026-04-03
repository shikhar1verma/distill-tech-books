---
title: "Set Theory and Operations"
chapter: 3
book: fluent-python
type: concept
slug: set-theory-and-operations
tags: [set, frozenset, union, intersection, difference, comprehension]
depends_on:
  - hashability
---

# Set Theory and Operations

## Overview

`set` (mutable) and `frozenset` (immutable, hashable) are built-in types backed by hash tables. They enforce element uniqueness and provide fast O(1) membership testing. Python implements the full suite of mathematical set operations as both operators and methods.

## Creating Sets

```python
# Set literal (NOT {} which is an empty dict)
s = {1, 2, 3}

# Empty set -- must use constructor
empty = set()

# From any iterable
s = set([1, 2, 2, 3])   # {1, 2, 3}
s = set('abracadabra')   # {'a', 'b', 'c', 'd', 'r'}

# frozenset (hashable, usable as dict key)
fs = frozenset([1, 2, 3])
```

**Performance note:** `{1, 2, 3}` is faster than `set([1, 2, 3])` because the literal uses the `BUILD_SET` bytecode directly, avoiding constructor lookup and list creation.

## Set Comprehensions

```python
from unicodedata import name
signs = {chr(i) for i in range(32, 256) if 'SIGN' in name(chr(i), '')}
```

## Removing Duplicates While Preserving Order

```python
items = ['spam', 'spam', 'eggs', 'bacon', 'eggs']
list(dict.fromkeys(items))  # ['spam', 'eggs', 'bacon']
```

## Set Operations

### Math operators (require both operands to be sets)

| Math | Python | Description |
|---|---|---|
| S union Z | `s \| z` | Union |
| S intersection Z | `s & z` | Intersection |
| S \ Z | `s - z` | Difference |
| S symmetric-diff Z | `s ^ z` | Symmetric difference |

### Methods (accept any iterable as argument)

```python
s.union(iterable)
s.intersection(iterable)
s.difference(iterable)
s.symmetric_difference(iterable)
```

### In-place variants (mutate the set)

```python
s |= other    # s.update(other)
s &= other    # s.intersection_update(other)
s -= other    # s.difference_update(other)
s ^= other    # s.symmetric_difference_update(other)
```

### Comparison predicates

| Math | Python | Method |
|---|---|---|
| S subset-of Z | `s <= z` | `s.issubset(z)` |
| S proper-subset Z | `s < z` | -- |
| S superset-of Z | `s >= z` | `s.issuperset(z)` |
| S proper-superset Z | `s > z` | -- |
| S disjoint Z | -- | `s.isdisjoint(z)` |

## Practical Example: Fast Membership Testing

```python
haystack = set(range(10_000_000))
needles = {3, 7, 42, 9_999_999}
found = needles & haystack   # near-instant
```

This is O(min(len(needles), len(haystack))) -- far faster than a loop.

## `frozenset`

Immutable and hashable. Can be used as a dict key or set element:

```python
fs = frozenset([1, 2, 3])
d = {fs: 'frozen key'}
groups = {frozenset([1, 2]), frozenset([3, 4])}
```

No literal syntax -- always use the `frozenset()` constructor.

## Practical Consequences of Hash Tables

- Elements must be hashable.
- Membership testing is O(1) average.
- Significant memory overhead (hash tables keep spare capacity).
- Element ordering depends on insertion order but is not reliable for reasoning.
- Adding elements can change the order of existing elements (due to hash table resizing).

## See Also

- [[hashability]] -- the hashability contract for set elements
- [[immutable-mappings-and-views]] -- dict views support set operations
- [[dict-comprehensions-unpacking-merging]] -- the related dictcomp syntax
