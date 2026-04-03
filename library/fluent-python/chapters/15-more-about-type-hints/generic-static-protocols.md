---
title: "Generic Static Protocols"
book: "Fluent Python"
chapter: 15
tags: [python, type-hints, protocols, generics, structural-typing]
related:
  - "[[generic-classes]]"
  - "[[variance]]"
  - "[[overloaded-signatures]]"
---

# Generic Static Protocols

> **One-sentence summary.** A generic protocol combines `Protocol` with type parameters (`Protocol[T_co]`) to define structural interfaces that are parameterized on types, typically covariant since protocols describe output behavior.

## How It Works

A static protocol (PEP 544) defines a structural interface: any class that implements the required methods is compatible, without explicit inheritance. Making a protocol **generic** adds a type parameter so the interface is parameterized.

The standard library's `SupportsAbs` is a good example:

```python
from typing import Protocol, TypeVar, runtime_checkable
from abc import abstractmethod

T_co = TypeVar("T_co", covariant=True)

@runtime_checkable
class SupportsAbs(Protocol[T_co]):
    __slots__ = ()

    @abstractmethod
    def __abs__(self) -> T_co: ...
```

Key elements:

1. **`Protocol[T_co]`** makes this a generic protocol parameterized on `T_co`.
2. **Covariant `T_co`** is appropriate because `__abs__` is an output (return value). A class whose `__abs__` returns `int` satisfies `SupportsAbs[float]` because `int <: float`.
3. **`@runtime_checkable`** enables `isinstance` checks at runtime.

Any class with an `__abs__` method automatically satisfies this protocol -- no inheritance needed:

```python
import math
from typing import NamedTuple

class Vector2d(NamedTuple):
    x: float
    y: float

    def __abs__(self) -> float:
        return math.hypot(self.x, self.y)

def is_unit(v: SupportsAbs[float]) -> bool:
    return math.isclose(abs(v), 1.0)

# Works with Vector2d, int, complex -- all have __abs__
assert is_unit(Vector2d(0, 1))
assert is_unit(1)
assert is_unit(complex(0.5, math.sqrt(3) / 2))
```

## In Practice

Generic protocols are useful when you want a function to accept any object that provides a specific method with a specific return type. The book's `RandomPicker` example defines a protocol for objects with a `pick()` method:

```python
@runtime_checkable
class RandomPicker(Protocol[T_co]):
    def pick(self) -> T_co: ...
```

Any class with a `pick` method returning a specific type satisfies this protocol. A `LottoBlower[int]` with `def pick(self) -> int` is a `RandomPicker[int]`. A card dealer with `def pick(self) -> str` is a `RandomPicker[str]`.

This is more precise than the non-generic version that would return `Any`. The generic version lets the type checker track what type `pick()` returns throughout the calling code.

Generic protocols are also the right choice when defining callback interfaces. For example, a `Comparator[T]` protocol could require a `__call__(self, a: T, b: T) -> int` method.

## Common Pitfalls

- **Choosing the wrong variance**: Protocols that only define output methods (return types) should use covariant parameters. If a protocol defines input methods (parameters), the type parameter for those inputs should be contravariant. Mixing both in one parameter requires invariance.
- **Forgetting `@runtime_checkable`**: Without this decorator, `isinstance(obj, MyProtocol)` raises `TypeError` at runtime. Add it if you need runtime checks.
- **Runtime `isinstance` is shallow**: Even with `@runtime_checkable`, the check only verifies method existence, not signatures or return types. It cannot detect that `pick()` returns `int` vs. `str`.

## See Also

- [[generic-classes]] -- the `Generic[T]` mechanism that protocols build on
- [[variance]] -- why protocol type parameters are typically covariant
- [[overloaded-signatures]] -- protocols like `SupportsLessThan` used in overloaded `max`
