---
title: "Dict Comprehensions, Unpacking, and Merging"
chapter: 3
book: fluent-python
type: concept
slug: dict-comprehensions-unpacking-merging
tags: [dict, comprehension, unpacking, merging, python3.9]
depends_on: []
---

# Dict Comprehensions, Unpacking, and Merging

## Overview

Python provides three modern syntactic tools for building and combining dicts: **dict comprehensions**, the `**` unpacking operator, and the `|` / `|=` merge operators (Python 3.9+). Together they make dict construction concise and expressive.

## Dict Comprehensions

A dict comprehension uses the `{key: value for ...}` syntax to build a dict from any iterable, analogous to a list comprehension.

```python
dial_codes = [(880, 'Bangladesh'), (55, 'Brazil'), (86, 'China')]
country_dial = {country: code for code, country in dial_codes}
# {'Bangladesh': 880, 'Brazil': 55, 'China': 86}
```

You can filter and transform inside the comprehension:

```python
{code: country.upper() for country, code in country_dial.items() if code < 70}
# {55: 'BRAZIL'}
```

## Unpacking Mappings with `**`

Since Python 3.5 (PEP 448), `**` can unpack multiple mappings in function calls and inside dict literals. Duplicate keys are resolved by last-write-wins:

```python
{'a': 0, **{'x': 1}, 'y': 2, **{'z': 3, 'x': 4}}
# {'a': 0, 'x': 4, 'y': 2, 'z': 3}
```

## Merging with `|` and `|=` (Python 3.9+)

The `|` operator creates a new dict from the union of two dicts. The `|=` operator updates a dict in place. Right-hand values win on collision:

```python
d1 = {'a': 1, 'b': 3}
d2 = {'a': 2, 'b': 4, 'c': 6}
d1 | d2   # {'a': 2, 'b': 4, 'c': 6}  -- new dict
d1 |= d2  # d1 is now {'a': 2, 'b': 4, 'c': 6}
```

## When to Use Which

| Technique | Use case |
|---|---|
| Dict comprehension | Build dict from iterable with filtering/transformation |
| `**` unpacking | Combine mappings inline, especially in function calls |
| `\|` / `\|=` | Merge two dicts cleanly (Python 3.9+) |
| `dict.update()` | Merge when you need to support pre-3.9 Python |

## See Also

- [[pattern-matching-mappings]] -- destructure dicts with match/case
- [[hashability]] -- keys must be hashable
- [[dict-variations]] -- specialized dict types in collections
