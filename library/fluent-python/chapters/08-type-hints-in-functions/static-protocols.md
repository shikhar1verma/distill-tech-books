---
title: "Static Protocols (Static Duck Typing)"
book: "Fluent Python"
chapter: 8
tags: [python, type-hints, Protocol, structural-typing, static-duck-typing]
related:
  - "[[typevar-and-parameterized-generics]]"
  - "[[gradual-typing-and-mypy]]"
  - "[[abcs-in-type-hints]]"
---

# Static Protocols (Static Duck Typing)

`typing.Protocol`, introduced in PEP 544 (Python 3.8), defines structural interfaces that the type checker verifies statically. A class is consistent-with a Protocol if it implements the required methods -- without inheriting from the Protocol, registering with it, or declaring any relationship. This bridges Python's duck typing tradition with static type checking, enabling what is called "static duck typing."

## How It Works

### Defining a Protocol

A Protocol is a subclass of `typing.Protocol` with one or more method signatures. The method bodies are `...` (ellipsis) -- they are just declarations.

```python
from typing import Protocol, Any

class SupportsLessThan(Protocol):
    def __lt__(self, other: Any) -> bool: ...
```

Any class that implements `__lt__` with a compatible signature is automatically consistent-with `SupportsLessThan` -- no inheritance or registration needed.

### Using Protocols with TypeVar

The real power emerges when you combine a Protocol with a bounded `TypeVar`:

```python
from collections.abc import Iterable
from typing import TypeVar

LT = TypeVar('LT', bound=SupportsLessThan)

def top(series: Iterable[LT], length: int) -> list[LT]:
    ordered = sorted(series, reverse=True)
    return ordered[:length]
```

This says: "`series` must be an iterable of items that support `<`, and the return list contains items of the same type." The type checker verifies this at every call site:

```python
top([4, 1, 5, 2, 6, 7, 3], 3)        # OK: int has __lt__
top("mango pear apple".split(), 2)     # OK: str has __lt__
top([object(), object()], 1)           # ERROR: object has no __lt__
```

### Why Not Just Use ABCs?

The problem that Protocols solve is the gap between what ABCs offer and what you actually need. Consider `sorted`: it requires elements that support `<`, but there is no ABC in the standard library that captures "has `__lt__`." You would have to use `Hashable` (wrong interface) or `Any` (no checking at all).

With Protocol, you define exactly the interface you need:

| Approach | Problem |
|----------|---------|
| `Iterable[Any]` | No checking -- allows unsortable types |
| `Iterable[Hashable]` | Wrong interface -- `__hash__` is not `__lt__` |
| `Iterable[SupportsLessThan]` | Exact match -- requires `__lt__` |

### Structural Subtyping

Protocol implements structural subtyping: a type is compatible based on its structure (what methods it has), not its name or inheritance tree. This is how duck typing has always worked at runtime. Protocol brings the same idea to static analysis.

```python
class Temperature:
    def __init__(self, value: float):
        self.value = value
    def __lt__(self, other: "Temperature") -> bool:
        return self.value < other.value

# Temperature never mentions SupportsLessThan, but it satisfies the protocol.
# The type checker accepts:
top([Temperature(72), Temperature(65), Temperature(80)], 2)
```

### Runtime Checkable Protocols

By default, Protocols are only used by type checkers. Adding `@runtime_checkable` lets you use them with `isinstance`:

```python
from typing import runtime_checkable, Protocol, Any

@runtime_checkable
class SupportsLessThan(Protocol):
    def __lt__(self, other: Any) -> bool: ...

isinstance(42, SupportsLessThan)        # True
isinstance("hello", SupportsLessThan)   # True
isinstance(object(), SupportsLessThan)  # False
```

Note: runtime `isinstance` checks only verify that the methods exist, not their signatures. Static type checking is more thorough.

## In Practice

- **Define Protocols for the exact interface you need.** Instead of reaching for an ABC that is "close enough," declare the precise set of methods your function requires.
- **Combine with bounded TypeVar** to preserve type information through generic functions. This is the most common and powerful pattern.
- **Use `@runtime_checkable` sparingly.** It is useful for defensive programming and debugging, but the static check is the primary value.
- **Protocols can have multiple methods.** A Protocol with `__lt__` and `__eq__` means "types that support both `<` and `==`."
- **Protocols can have attributes.** You can declare instance attributes like `name: str` in a Protocol body.
- **Protocols can extend other Protocols.** Use inheritance between Protocol classes to build up complex interfaces from simple ones.

## Common Pitfalls

- **Forgetting that Protocol is structural**: You do NOT need to inherit from a Protocol for a class to satisfy it. If your class has the right methods, it qualifies automatically.
- **Confusing Protocol with ABC**: ABCs use nominal subtyping (you must inherit or register). Protocols use structural subtyping (just implement the methods). They solve different problems.
- **Overusing Protocols**: Not every function parameter needs a Protocol. For simple cases, concrete types or existing ABCs work fine. Protocols shine when no existing type captures the interface you need.
- **`@runtime_checkable` limitations**: It only checks method existence at runtime, not argument types or return types. A class with `__lt__(self)` (wrong signature) would pass `isinstance` but fail type checking.
- **Protocol methods must have `...` bodies**: In the Protocol definition, use `...` (not `pass`, not a real implementation) for method bodies.

## See Also

- [[typevar-and-parameterized-generics]] -- TypeVar bounded by Protocol is the key pattern
- [[gradual-typing-and-mypy]] -- How duck typing and nominal typing coexist
- [[abcs-in-type-hints]] -- The nominal alternative to structural typing
- PEP 544 -- Protocols: Structural subtyping (static duck typing)
- Chapter 13 of Fluent Python -- Deep dive into Protocols vs ABCs
