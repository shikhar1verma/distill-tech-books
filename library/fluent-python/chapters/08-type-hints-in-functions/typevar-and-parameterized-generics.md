---
title: "TypeVar and Parameterized Generics"
book: "Fluent Python"
chapter: 8
tags: [python, type-hints, TypeVar, generics, restricted-typevar, bounded-typevar]
related:
  - "[[abcs-in-type-hints]]"
  - "[[static-protocols]]"
  - "[[any-optional-union]]"
---

# TypeVar and Parameterized Generics

`TypeVar` creates type variables that let functions express relationships between input and output types -- for example, "the return type matches the input element type." Restricted TypeVars limit the variable to specific named types, while bounded TypeVars accept any subtype of an upper bound. This is the mechanism that makes generic functions truly type-safe.

## How It Works

### Basic TypeVar

A parameterized generic uses `TypeVar` to declare a type variable that gets bound to a specific type at each call site:

```python
from collections.abc import Sequence
from typing import TypeVar
from random import shuffle

T = TypeVar('T')

def sample(population: Sequence[T], size: int) -> list[T]:
    if size < 1:
        raise ValueError('size must be >= 1')
    result = list(population)
    shuffle(result)
    return result[:size]
```

When called with `tuple[int, ...]`, `T` binds to `int` and the return type is `list[int]`. When called with `list[str]`, `T` binds to `str` and the return type is `list[str]`. The type checker tracks this binding automatically.

Without `TypeVar`, you would have to return `list[Any]`, losing all type information about the elements.

### Why TypeVar Exists

Python's type hints were added via the `typing` module without changing the language itself. The `T` in `Sequence[T]` must be a defined name in the current namespace -- otherwise the interpreter would need deep syntax changes. That is why `TypeVar('T')` is needed as an explicit declaration. Languages like Java, C#, and TypeScript define type parameters inline (e.g., `<T>`) and do not need an equivalent of `TypeVar`.

### Restricted TypeVar

A restricted TypeVar is constrained to specific types given as positional arguments:

```python
from decimal import Decimal
from fractions import Fraction
from typing import TypeVar

NumberT = TypeVar('NumberT', float, Decimal, Fraction)

def mode(data: Iterable[NumberT]) -> NumberT:
    pairs = Counter(data).most_common(1)
    if len(pairs) == 0:
        raise ValueError('no mode for empty data')
    return pairs[0][0]
```

Here `NumberT` can only be `float`, `Decimal`, or `Fraction`. If you call `mode` with a `list[float]`, the return type is `float`. Calling it with `list[str]` would be a type error.

The limitation: you cannot keep adding types forever. If `mode` should also work with `str`, you either add `str` to the restriction list (misnamed as `NumberT`) or switch to a bounded TypeVar.

### Bounded TypeVar

A bounded TypeVar accepts any type that is a subtype of the given bound:

```python
from collections.abc import Hashable, Iterable
from collections import Counter
from typing import TypeVar

HashableT = TypeVar('HashableT', bound=Hashable)

def mode(data: Iterable[HashableT]) -> HashableT:
    pairs = Counter(data).most_common(1)
    if len(pairs) == 0:
        raise ValueError('no mode for empty data')
    return pairs[0][0]
```

Now `mode` works with any hashable type: `int`, `str`, `float`, `tuple`, custom classes -- anything that implements `__hash__`. The return type preserves the specific input type.

### Comparison

| Feature | Restricted | Bounded |
|---------|-----------|---------|
| Declaration | `TypeVar('T', float, str)` | `TypeVar('T', bound=Hashable)` |
| Accepted types | Exactly the listed types | Any subtype of the bound |
| Best for | Small, closed set of types | Open-ended type hierarchies |
| Example | `float`, `Decimal`, `Fraction` | Anything `Hashable` |

### The AnyStr Predefined TypeVar

The `typing` module provides a built-in restricted TypeVar:

```python
from typing import AnyStr
# Equivalent to: AnyStr = TypeVar('AnyStr', bytes, str)

def concat(a: AnyStr, b: AnyStr) -> AnyStr:
    return a + b
```

This ensures that both arguments and the return value are either all `str` or all `bytes` -- you cannot mix them.

## In Practice

- **Use unrestricted TypeVar** when the function works with truly any type (like `sample` above).
- **Use restricted TypeVar** when you have a small, known set of types and want the return type to match the input type.
- **Use bounded TypeVar** when you need a specific interface (like `Hashable`, `SupportsLessThan`) but want to preserve the concrete type in the return.
- **Combine with [[static-protocols]]** for maximum power: define a Protocol, then use it as the bound for a TypeVar.
- **Name TypeVars clearly**: `T` for general-purpose, `NumberT` for numeric contexts, `HashableT` for hashable contexts. The string argument to `TypeVar()` must match the variable name.

## Common Pitfalls

- **The string must match the variable name**: `T = TypeVar('T')` is correct. `T = TypeVar('U')` is wrong and will confuse type checkers.
- **Confusing `bound=` with restriction**: `TypeVar('T', bound=float)` means "any subtype of float." `TypeVar('T', float, int)` means "exactly float or int."
- **Using TypeVar in only one position**: If `T` appears only in the parameter list but not in the return type (or vice versa), it serves no purpose -- you could just use `Any` or a concrete type.
- **The `bound` keyword is poorly named**: It means "upper boundary" not "binding a value." Think of it as `boundary=Hashable`.
- **Forgetting that `int` is consistent-with `float`**: If your bound is `float`, both `int` and `float` values are accepted.

## See Also

- [[static-protocols]] -- Define custom structural interfaces to use as TypeVar bounds
- [[abcs-in-type-hints]] -- ABCs as another source of bounds for TypeVars
- [[any-optional-union]] -- `Any` vs the precision that TypeVar provides
- PEP 484 -- Type Hints (introduces TypeVar)
- Chapter 15 of Fluent Python -- Covers covariant and contravariant TypeVars
