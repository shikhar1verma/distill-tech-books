---
title: "Type Hints 101 for Data Classes"
slug: type-hints-101
chapter: 5
book: "Fluent Python"
type: theory-heavy
depends_on:
  - typed-named-tuples
tags: [type-hints, annotations, PEP-526, PEP-484, mypy, static-analysis]
---

# Type Hints 101 for Data Classes

Type hints (a.k.a. type annotations) declare the expected types of function arguments, return values, variables, and attributes. Both `typing.NamedTuple` and `@dataclass` rely on the variable annotation syntax from PEP 526 to declare fields.

## No Runtime Effect

The most important thing to understand: **type hints have zero runtime effect**. Python reads them at import time to build `__annotations__`, but the bytecode compiler and interpreter never enforce them.

```python
from typing import NamedTuple

class Coordinate(NamedTuple):
    lat: float
    lon: float

trash = Coordinate('Ni!', None)  # No error at runtime!
```

Type hints are "documentation that can be verified by IDEs and type checkers" like Mypy, Pyright, or the PyCharm built-in checker. These are static analysis tools that check source code "at rest."

## Variable Annotation Syntax (PEP 526)

The basic syntax:

```python
var_name: some_type
var_name: some_type = a_value
```

Acceptable types in data class declarations:
- Concrete classes: `str`, `int`, `float`, `FrenchDeck`
- Parameterized collections: `list[int]`, `tuple[str, float]`
- `typing.Optional[str]` (equivalent to `str | None` in 3.10+)

## How Annotations Behave in Different Contexts

### Plain class

```python
class DemoPlain:
    a: int           # goes in __annotations__, but no class attribute created
    b: float = 1.1   # goes in __annotations__ AND becomes class attribute
    c = 'spam'       # class attribute only, no annotation
```

- `DemoPlain.a` raises `AttributeError`
- `DemoPlain.b` returns `1.1`
- `DemoPlain.__annotations__` is `{'a': int, 'b': float}`

### `typing.NamedTuple`

- `a` and `b` become `_tuplegetter` descriptors (read-only instance fields)
- `c` is still a plain class attribute

### `@dataclass`

- `a` has no class-level attribute, but becomes a required `__init__` parameter
- `b` is a class attribute holding the default; also becomes an `__init__` parameter
- `c` is a plain class attribute, ignored by `@dataclass`

## Reading Annotations

Do **not** read `__annotations__` directly. Use:
- `typing.get_type_hints(MyClass)` (Python 3.5+)
- `inspect.get_annotations(MyClass)` (Python 3.10+)

These functions resolve forward references and handle other edge cases.

## See Also

- [[typed-named-tuples]] -- how NamedTuple uses annotations
- [[dataclass-decorator-and-fields]] -- how @dataclass uses annotations
- [[data-class-builders-overview]] -- the big picture
