---
title: "Implementing Generic Classes"
book: "Fluent Python"
chapter: 15
tags: [python, type-hints, generics, typevar, typing]
related:
  - "[[variance]]"
  - "[[generic-static-protocols]]"
  - "[[overloaded-signatures]]"
---

# Implementing Generic Classes

> **One-sentence summary.** A generic class is parameterized with `TypeVar` and inherits from `Generic[T]`, allowing users to write `MyClass[int]` so the type checker enforces that all methods using `T` are consistent with the actual type parameter.

## How It Works

To create a generic class, you need two ingredients:

1. **A `TypeVar`** that serves as the formal type parameter.
2. **`Generic[T]`** as a base class (or mixin) that registers the class as generic.

```python
from typing import TypeVar, Generic
from collections.abc import Iterable

T = TypeVar("T")

class LottoBlower(Generic[T]):
    def __init__(self, items: Iterable[T]) -> None:
        self._balls = list(items)

    def load(self, items: Iterable[T]) -> None:
        self._balls.extend(items)

    def pick(self) -> T:
        import random
        position = random.randrange(len(self._balls))
        return self._balls.pop(position)

    def inspect(self) -> tuple[T, ...]:
        return tuple(self._balls)
```

When a user writes `machine = LottoBlower[int](range(1, 11))`, the type checker binds `T` to `int` throughout the class. Calling `machine.load("ABC")` produces an error because `str.__iter__` yields `str`, not `int`.

Generic class declarations often involve multiple inheritance because you may need to subclass both a domain ABC and `Generic[T]`:

```python
class LottoBlower(Tombola, Generic[T]):
    ...
```

## In Practice

Generic classes are the foundation for type-safe containers and abstractions. The standard library uses them extensively: `list[T]`, `dict[K, V]`, `set[T]`, `Mapping[K, V]`, `Iterator[T]`, etc.

When building your own generic classes, keep the jargon straight:

| Term | Example |
|---|---|
| **Generic type** | `LottoBlower[T]` -- the class with unbound parameters |
| **Formal type parameter** | `T` in the class definition |
| **Parameterized type** | `LottoBlower[int]` -- bound to a concrete type |
| **Actual type parameter** | `int` in `LottoBlower[int]` |

By default, `TypeVar` creates an **invariant** parameter. This means `LottoBlower[int]` is not compatible with `LottoBlower[float]`, even though `int` is a subtype of `float`. For different behavior, see variance.

## Common Pitfalls

- **Forgetting `Generic[T]`**: Without it, the `[]` syntax does not work and the type checker treats `T` as a regular type variable without binding.
- **Using the same TypeVar in unrelated classes**: Each `TypeVar` instance is independent. If two generic classes should have independent type parameters, they can share the same `TypeVar` object. But if they appear together (e.g., in a function signature), the checker binds them independently.
- **Mutable generic classes should be invariant**: If `T` appears in both input positions (method arguments) and output positions (return types), the class must be invariant. This is the default and the safe choice.

## See Also

- [[variance]] -- how to make generic classes covariant or contravariant
- [[generic-static-protocols]] -- combining generics with structural typing
- [[overloaded-signatures]] -- overloads often use `TypeVar` for precise return types
