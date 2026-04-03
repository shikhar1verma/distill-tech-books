---
title: "Overloaded Signatures with @overload"
book: "Fluent Python"
chapter: 15
tags: [python, type-hints, overload, typing]
related:
  - "[[typeddict]]"
  - "[[type-casting]]"
  - "[[generic-classes]]"
---

# Overloaded Signatures with @overload

> **One-sentence summary.** The `@typing.overload` decorator declares multiple type signatures for a single function, enabling the type checker to infer the precise return type based on the types of the arguments.

## How It Works

Python functions often accept different combinations of argument types and return different types accordingly. Without `@overload`, the best a type hint can do is declare a broad `Union` return type, losing precision. With `@overload`, each call pattern gets its own signature, and the type checker matches the actual call to the right overload.

The pattern has three parts:

1. **Overloaded signatures** -- decorated with `@overload`, each with a function body of just `...` (ellipsis). These exist purely for the type checker.
2. **The actual implementation** -- the final definition of the function with the real body but **no type annotations**.
3. **Matching** -- the type checker tries each overloaded signature top-to-bottom and uses the first one that matches.

```python
from typing import overload

@overload
def double(x: int) -> int: ...

@overload
def double(x: str) -> str: ...

def double(x):
    return x * 2

# The type checker knows:
#   double(10)   -> int
#   double("ha") -> str
```

In stub files (`.pyi`), only the overloaded signatures appear since the implementation lives elsewhere. In regular `.py` modules, both the overloaded signatures and the implementation must be in the same file, with overloads immediately before the implementation.

## In Practice

The canonical use case from the standard library is `sum`. The return type depends on whether a `start` argument is provided: without `start`, the result is `Union[T, int]` (the default start is `0`); with `start` of type `S`, the result is `Union[T, S]`.

A more complex real-world example is `max`, which requires six overloaded signatures to cover all combinations of positional arguments vs. iterable, with or without `key`, and with or without `default`. The type stubs on typeshed use a `SupportsLessThan` protocol with a bounded `TypeVar` to ensure that only comparable items are accepted.

Overloads are also useful when wrapping APIs whose return type depends on a flag argument (e.g., `open()` returning `TextIO` or `BufferedReader` depending on the mode string).

## Common Pitfalls

- **Forgetting the implementation**: The overloaded signatures alone are not callable. You must provide the final function definition without `@overload` and without type hints.
- **Overlapping signatures**: If two overloads could match the same call, the first one wins. Order matters.
- **Over-engineering**: The `max` example needs six overloads for full coverage. For simple functions, a `Union` return type may be good enough. Aim for 100% annotation coverage only when the payoff justifies the complexity.

## See Also

- [[type-casting]] -- another tool for guiding the type checker when annotations fall short
- [[generic-classes]] -- overloads often use `TypeVar` for parameterized return types
- [[generic-static-protocols]] -- protocols like `SupportsLessThan` used in the `max` overloads
