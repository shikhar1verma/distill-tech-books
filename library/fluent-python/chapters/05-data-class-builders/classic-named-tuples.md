---
title: "Classic Named Tuples (collections.namedtuple)"
slug: classic-named-tuples
chapter: 5
book: "Fluent Python"
type: code-heavy
depends_on:
  - data-class-builders-overview
tags: [namedtuple, collections, immutable, tuple, factory-function]
---

# Classic Named Tuples (`collections.namedtuple`)

`collections.namedtuple` is a factory function that builds subclasses of `tuple` enhanced with field names, a class name, and an informative `__repr__`. Available since Python 2.6.

## Creating a Named Tuple

```python
from collections import namedtuple

City = namedtuple('City', 'name country population coordinates')
tokyo = City('Tokyo', 'JP', 36.933, (35.689722, 139.691667))

tokyo.population   # 36.933  -- access by name
tokyo[1]           # 'JP'    -- access by index (it's a tuple)
```

Two parameters are required: a class name and field names (iterable of strings or a single space-delimited string).

## Key Attributes and Methods

| Attribute/Method | Purpose |
|---|---|
| `._fields` | Tuple of field name strings |
| `._field_defaults` | Dict of field names to default values |
| `._make(iterable)` | Class method: build instance from iterable |
| `._asdict()` | Return an `OrderedDict` (Python < 3.8) or `dict` |
| `._replace(**kwargs)` | Return new instance with specified fields replaced |

```python
City._fields              # ('name', 'country', 'population', 'coordinates')
delhi_data = ('Delhi NCR', 'IN', 21.935, (28.61, 77.21))
delhi = City._make(delhi_data)
delhi._asdict()           # {'name': 'Delhi NCR', ...}
```

## Defaults (Python 3.7+)

The `defaults` keyword argument provides default values for the N rightmost fields:

```python
Coordinate = namedtuple('Coordinate', 'lat lon reference', defaults=['WGS84'])
Coordinate(0, 0)                  # Coordinate(lat=0, lon=0, reference='WGS84')
Coordinate._field_defaults        # {'reference': 'WGS84'}
```

## Memory Efficiency

Each instance uses exactly the same memory as a plain tuple -- field names are stored on the class, not on instances. This makes named tuples very memory-efficient for large collections of records.

## Injecting Methods (Hack)

Since `namedtuple` does not support class-body syntax, you can add methods by assigning functions to class attributes:

```python
Card = namedtuple('Card', ['rank', 'suit'])
Card.suit_values = dict(spades=3, hearts=2, diamonds=1, clubs=0)

def spades_high(card):
    rank_value = 'A23456789TJQKA'.index(card.rank[0])
    return rank_value * len(card.suit_values) + card.suit_values[card.suit]

Card.overall_rank = spades_high
```

This works but is a hack -- prefer [[typed-named-tuples]] or [[dataclass-decorator-and-fields]] when you need methods.

## See Also

- [[data-class-builders-overview]] -- comparison of all three builders
- [[typed-named-tuples]] -- the typed alternative with class syntax
