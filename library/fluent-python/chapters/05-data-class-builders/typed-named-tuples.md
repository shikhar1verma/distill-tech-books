---
title: "Typed Named Tuples (typing.NamedTuple)"
slug: typed-named-tuples
chapter: 5
book: "Fluent Python"
type: code-heavy
depends_on:
  - classic-named-tuples
tags: [NamedTuple, typing, immutable, tuple, type-hints, class-syntax]
---

# Typed Named Tuples (`typing.NamedTuple`)

`typing.NamedTuple` extends classic named tuples with PEP 526 class-statement syntax and type annotations. The result is still an immutable `tuple` subclass with the same runtime behavior as `collections.namedtuple`.

## Class Syntax (Python 3.6+)

```python
from typing import NamedTuple

class Coordinate(NamedTuple):
    lat: float
    lon: float
    reference: str = 'WGS84'

    def __str__(self):
        ns = 'N' if self.lat >= 0 else 'S'
        we = 'E' if self.lon >= 0 else 'W'
        return f'{abs(self.lat):.1f} {ns}, {abs(self.lon):.1f} {we}'
```

Key advantages over `collections.namedtuple`:
- **Type annotations** on every field
- **Class body** for adding methods and docstrings naturally
- **Default values** declared inline with `field: type = default`

## Functional Syntax

You can also use a function call, similar to `collections.namedtuple`:

```python
Coordinate = NamedTuple('Coordinate', [('lat', float), ('lon', float)])
# or with keyword arguments:
Coordinate = NamedTuple('Coordinate', lat=float, lon=float)
```

## The Metaclass Trick

Although `NamedTuple` appears in the class statement as a superclass, it is **not** an actual base class:

```python
issubclass(Coordinate, NamedTuple)  # False!
issubclass(Coordinate, tuple)       # True
```

`typing.NamedTuple` uses metaclass machinery to customize class creation. The resulting class is a `tuple` subclass -- the `NamedTuple` "superclass" is just a syntactic vehicle.

## Annotations Behavior

Every field must have a type annotation. An attribute declared without a type annotation (e.g., `c = 'spam'`) becomes a plain class attribute, not a named tuple field:

```python
class DemoNT(NamedTuple):
    a: int             # field, with descriptor
    b: float = 1.1     # field with default
    c = 'spam'         # plain class attribute, NOT a field

DemoNT.__annotations__  # {'a': int, 'b': float}  -- no 'c'
```

The `a` and `b` class attributes are `_tuplegetter` descriptors (similar to property getters) that retrieve values from the underlying tuple by position.

## Same API as Classic Named Tuples

`typing.NamedTuple` classes have exactly the same methods as `collections.namedtuple`:
- `_fields`, `_field_defaults`, `_make()`, `_asdict()`, `_replace()`

The only addition is `__annotations__`, holding the type hints.

## See Also

- [[classic-named-tuples]] -- the original, simpler variant
- [[type-hints-101]] -- how type annotations work (and don't) at runtime
- [[data-class-builders-overview]] -- comparison of all three builders
