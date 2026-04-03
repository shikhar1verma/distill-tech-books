---
title: "Generic Collections and Tuple Types"
book: "Fluent Python"
chapter: 8
tags: [python, type-hints, generics, collections, tuple, NamedTuple]
related:
  - "[[any-optional-union]]"
  - "[[abcs-in-type-hints]]"
  - "[[typevar-and-parameterized-generics]]"
---

# Generic Collections and Tuple Types

Generic type hints like `list[str]` and `dict[str, int]` constrain element types in collections, turning Python's heterogeneous containers into precisely typed structures for static analysis. Tuple has three distinct annotation forms -- fixed-field records, named tuples, and variable-length immutable sequences -- each serving a different purpose.

## How It Works

### Generic Collections

Since Python 3.9, you can parameterize built-in collection types directly with `[]`:

```python
def tokenize(text: str) -> list[str]:
    return text.upper().split()
```

This tells the type checker that `tokenize` returns a `list` where every element is a `str`. The annotations `stuff: list` and `stuff: list[Any]` mean the same thing: a list of objects of any type.

Common generic collection forms:

| Type | Annotation |
|------|-----------|
| List of strings | `list[str]` |
| Set of integers | `set[int]` |
| Dict with str keys, int values | `dict[str, int]` |
| Deque of floats | `collections.deque[float]` |
| Frozen set of str | `frozenset[str]` |

For Python 3.7-3.8, add `from __future__ import annotations` to use the `[]` notation. For Python 3.5-3.6, use `typing.List`, `typing.Dict`, etc. (deprecated since 3.9).

### Generic Mappings

Mappings take two type parameters -- key and value:

```python
import unicodedata
import re

RE_WORD = re.compile(r'\w+')

def name_index(start: int = 32, end: int = 128) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for char in (chr(i) for i in range(start, end)):
        if name := unicodedata.name(char, ''):
            for word in RE_WORD.findall(name.upper()):
                index.setdefault(word, set()).add(char)
    return index
```

Note that local variables sometimes need explicit annotation (like `index` above) because the type checker cannot always infer the type of an empty collection.

### Tuple Types -- Three Forms

**1. Tuples as records (fixed fields):**

Each position has a specific type. The number of elements is fixed.

```python
# A coordinate pair: exactly two floats
def geohash(lat_lon: tuple[float, float]) -> str:
    ...

# A city record: name, population, country
city: tuple[str, float, str] = ('Shanghai', 24.28, 'China')
```

**2. Tuples as named records:**

`typing.NamedTuple` creates a tuple subclass with named fields. A `Coordinate` is consistent-with `tuple[float, float]`.

```python
from typing import NamedTuple

class Coordinate(NamedTuple):
    lat: float
    lon: float

shanghai = Coordinate(31.23, 121.47)
```

**3. Tuples as immutable sequences (variable-length):**

Use a single type followed by `...` to indicate any number of elements of the same type.

```python
# A tuple of zero or more ints
numbers: tuple[int, ...] = (1, 2, 3, 4, 5)

def columnize(sequence: list[str], num_columns: int = 0) -> list[tuple[str, ...]]:
    if num_columns == 0:
        num_columns = round(len(sequence) ** 0.5)
    num_rows, remainder = divmod(len(sequence), num_columns)
    num_rows += bool(remainder)
    return [tuple(sequence[i::num_rows]) for i in range(num_rows)]
```

The annotations `stuff: tuple[Any, ...]` and `stuff: tuple` mean the same thing: a tuple of unspecified length with objects of any type.

## In Practice

- **Use `list[str]` for return types** and `Sequence[str]` for parameter types (see [[abcs-in-type-hints]]).
- **Prefer `NamedTuple` over plain tuples** for records with more than 2-3 fields. Named fields make code self-documenting and the type becomes reusable.
- **Type aliases** improve readability for complex generic types:
  ```python
  from typing import TypeAlias
  
  FromTo: TypeAlias = tuple[str, str]
  
  def zip_replace(text: str, changes: Iterable[FromTo]) -> str:
      ...
  ```
- **`dict` vs `TypedDict`**: For dictionaries used as records with string keys and heterogeneous value types, consider `TypedDict` (covered in Chapter 15).
- **Annotate local variables** when initializing empty collections. Mypy cannot infer the element type of `{}` or `[]` without help.

## Common Pitfalls

- **Confusing `tuple[int]` with `tuple[int, ...]`**: `tuple[int]` means a tuple with exactly one `int` element. `tuple[int, ...]` means a tuple with any number of `int` elements.
- **Using `list[int]` for parameters** instead of `Sequence[int]`: This unnecessarily restricts callers to passing actual `list` objects (or subclasses). A `tuple` or custom sequence would be rejected.
- **Forgetting `from __future__ import annotations`** on Python 3.7-3.8: Without it, `list[str]` raises a `TypeError` at runtime (though the annotation is never evaluated at runtime in Python 3.10+).
- **`array.array` cannot be precisely typed**: The `typecode` that determines whether an array holds ints or floats is a runtime value, not expressible in the current type system.

## See Also

- [[abcs-in-type-hints]] -- Why ABCs are better than concrete types for parameters
- [[any-optional-union]] -- `Any` as the default element type for unparameterized collections
- [[typevar-and-parameterized-generics]] -- Making generic functions that preserve element types
- PEP 585 -- Type Hinting Generics In Standard Collections
