---
title: "Abstract Base Classes in Type Hints"
book: "Fluent Python"
chapter: 8
tags: [python, type-hints, ABCs, Mapping, Sequence, Iterable, Postel-law]
related:
  - "[[generic-collections-and-tuples]]"
  - "[[typevar-and-parameterized-generics]]"
  - "[[static-protocols]]"
---

# Abstract Base Classes in Type Hints

Using ABCs like `Mapping`, `Sequence`, and `Iterable` from `collections.abc` as parameter types follows Postel's law -- "Be conservative in what you send, be liberal in what you accept." By accepting the most general type that supports the needed operations, you make your functions more flexible and your type annotations more accurate.

## How It Works

The core principle is asymmetric:

- **Parameters**: Use abstract types (`Mapping`, `Sequence`, `Iterable`) to accept the widest range of inputs.
- **Return types**: Use concrete types (`dict`, `list`, `set`) to give callers precise information about what they receive.

### Mapping vs dict

```python
from collections.abc import Mapping

# GOOD: Accepts dict, defaultdict, OrderedDict, ChainMap, UserDict subclass...
def name2hex(name: str, color_map: Mapping[str, int]) -> str:
    code = color_map.get(name.lower(), 0x000000)
    return f"#{code:06x}"

# BAD: Only accepts dict and its subclasses
def name2hex_strict(name: str, color_map: dict[str, int]) -> str:
    code = color_map.get(name.lower(), 0x000000)
    return f"#{code:06x}"
```

The `dict` annotation rejects `collections.UserDict` subclasses because `UserDict` is not a subclass of `dict` -- they are siblings under `abc.MutableMapping`. Using `Mapping` avoids this false rejection.

If the function does not mutate the mapping, use `Mapping` (read-only). If it must call methods like `setdefault`, `pop`, or `update`, use `MutableMapping`.

### Sequence vs list

```python
from collections.abc import Sequence

# Accepts list, tuple, str, range, memoryview, etc.
def first_item(items: Sequence[str]) -> str:
    return items[0]
```

Use `Sequence` when you need indexing and `len()`. Use `list` only in return types or when you genuinely need list-specific operations.

### Iterable -- Maximum Flexibility

```python
from collections.abc import Iterable

FromTo = tuple[str, str]

def zip_replace(text: str, changes: Iterable[FromTo]) -> str:
    for from_, to in changes:
        text = text.replace(from_, to)
    return text
```

`Iterable` is the most permissive: it accepts lists, tuples, generators, sets, and any object with `__iter__`. Use it when you only need to iterate through the items once.

### Iterable vs Sequence

Choose based on what operations you need:

| You need... | Use |
|-------------|-----|
| Just iteration (`for x in items`) | `Iterable` |
| Iteration + `len()` + indexing | `Sequence` |
| All of above + mutation (`append`, `pop`) | `MutableSequence` |

`math.fsum` uses `Iterable[float]` because it only needs to loop through the values. The `columnize` function needs `Sequence` because it must call `len()` to compute the layout.

### The Numeric Tower

The `numbers` ABCs (`Number`, `Complex`, `Real`, `Rational`, `Integral`) work for runtime `isinstance` checks but are NOT supported by static type checkers. PEP 484 instead declares special rules: `int` is consistent-with `float`, and `float` is consistent-with `complex`.

For annotating numeric parameters:
1. Use `int`, `float`, or `complex` directly.
2. Use `Union[float, Decimal, Fraction]` for multiple numeric types.
3. Use numeric protocols like `SupportsFloat` for maximum generality (see [[static-protocols]]).

## In Practice

- **Default to ABCs for parameters** unless you have a specific reason to require a concrete type.
- **Return concrete types** so callers know exactly what methods are available.
- **Use `Iterable` for generator-friendly APIs**: This allows callers to pass generators that yield items lazily, saving memory for large datasets.
- **Type aliases** help readability:
  ```python
  from typing import TypeAlias
  ColorMap: TypeAlias = Mapping[str, int]
  ```
- **Import from `collections.abc`** (not `typing`) on Python 3.9+. The `typing` equivalents (`typing.Mapping`, `typing.Sequence`) are deprecated.

## Common Pitfalls

- **Using `dict` for parameters**: Rejects `UserDict`, `ChainMap`, and other valid mapping types. Use `Mapping` or `MutableMapping`.
- **Using `list` for parameters**: Rejects tuples, ranges, and custom sequences. Use `Sequence` or `Iterable`.
- **Returning `Iterable` or `Sequence`**: Too vague for return types. The caller cannot know whether the result supports indexing, mutation, or re-iteration. Return `list`, `dict`, `set`, etc.
- **Using `numbers.Real` in type hints**: Not supported by type checkers. Use `float` (which also accepts `int`) or a `Union`.
- **Forgetting that `str` is a `Sequence[str]`**: If you annotate `items: Sequence[str]`, a single string is a valid argument (each character is a `str`). This can lead to subtle bugs when you expect a list of strings but receive one string iterated character by character.

## See Also

- [[generic-collections-and-tuples]] -- Parameterizing concrete collection types
- [[typevar-and-parameterized-generics]] -- Preserving element types through generic functions
- [[static-protocols]] -- An alternative to ABCs for defining interfaces structurally
- PEP 484 -- Type Hints
- Postel's Law (Robustness Principle): RFC 761
