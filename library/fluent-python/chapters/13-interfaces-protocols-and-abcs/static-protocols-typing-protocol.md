---
title: "Static Protocols with typing.Protocol"
chapter: 13
slug: static-protocols-typing-protocol
type: code-heavy
depends_on:
  - typing-map-four-approaches
  - dynamic-protocols-and-duck-typing
tags:
  - typing-Protocol
  - PEP-544
  - static-duck-typing
  - runtime-checkable
  - structural-subtyping
  - SupportsFloat
---

# Static Protocols with typing.Protocol

`typing.Protocol` (PEP 544, Python 3.8) brings **static duck typing** to Python. You define a Protocol subclass with required methods, and any class implementing those methods is considered *consistent-with* the protocol by static type checkers -- no inheritance or registration needed.

## The Typed double Function

Before protocols, there was no way to type-hint `double(x)` that works with `str`, `list`, `int`, `float`, and `Fraction`:

```python
from typing import TypeVar, Protocol

T = TypeVar('T')

class Repeatable(Protocol):
    def __mul__(self: T, repeat_count: int) -> T: ...

RT = TypeVar('RT', bound=Repeatable)

def double(x: RT) -> RT:
    return x * 2
```

The nominal type of the argument is irrelevant -- it just needs to *quack* (implement `__mul__`). This is why PEP 544 is titled "Protocols: Structural subtyping (static duck typing)."

## @runtime_checkable

By default, Protocol subclasses only work with static type checkers. Adding `@runtime_checkable` enables `isinstance`/`issubclass` checks:

```python
from typing import runtime_checkable, Protocol

@runtime_checkable
class RandomPicker(Protocol):
    def pick(self) -> Any: ...

class SimplePicker:
    def pick(self):
        return 42

isinstance(SimplePicker(), RandomPicker)  # True
```

### Built-in runtime-checkable protocols

Python 3.9+ provides seven runtime-checkable protocols in `typing`:

| Protocol | Abstract Method |
|---|---|
| `SupportsComplex` | `__complex__` |
| `SupportsFloat` | `__float__` |
| `SupportsInt` | `__int__` |
| `SupportsIndex` | `__index__` |
| `SupportsBytes` | `__bytes__` |
| `SupportsAbs` | `__abs__` |
| `SupportsRound` | `__round__` |

### Limitations of runtime checks

Runtime `isinstance` checks against protocols only verify **method presence**, not:

- Method signatures
- Return types
- Type annotations

This can produce misleading results. For example, in Python 3.9, `complex` has a `__float__` method that only raises `TypeError`, yet `isinstance(3+4j, SupportsFloat)` returns `True`.

**Best practice at runtime:** Use duck typing (`try/except`) rather than `isinstance` with protocols:

```python
# Prefer this:
try:
    c = complex(o)
except TypeError:
    raise TypeError('o must be convertible to complex')

# Over this:
if isinstance(o, SupportsComplex):
    c = complex(o)
```

## Supporting a Static Protocol

To make your class work with a static protocol, just implement the required methods:

```python
class Vector2d:
    def __complex__(self) -> complex:
        return complex(self.x, self.y)

    def __abs__(self) -> float:
        return math.hypot(self.x, self.y)
```

No import of `SupportsComplex` or `SupportsAbs` is needed. The class supports the protocol by implementing the methods -- static duck typing in action.

## Defining a Custom Protocol

```python
from typing import Protocol, runtime_checkable, Any

@runtime_checkable
class RandomPicker(Protocol):
    def pick(self) -> Any: ...
```

The class implementing it needs no awareness of the protocol:

```python
class SimplePicker:
    def __init__(self, items):
        self._items = list(items)

    def pick(self):
        return self._items.pop()

# SimplePicker is consistent-with RandomPicker
# No inheritance, no registration
```

## Extending a Protocol

Derive a new protocol rather than adding methods to an existing one:

```python
@runtime_checkable
class LoadableRandomPicker(RandomPicker, Protocol):
    def load(self, iterable) -> None: ...
```

**Caveats when extending:**

1. Apply `@runtime_checkable` again -- it is not inherited.
2. Every protocol must explicitly name `typing.Protocol` as a base class (in addition to the parent protocol). This differs from normal Python inheritance.
3. Only declare the *new* methods; inherited methods come from the parent protocol.

## The numbers ABCs vs. Numeric Protocols

| Approach | Pros | Cons |
|---|---|---|
| `numbers` ABCs | Work at runtime; NumPy types registered | Not recognized by static type checkers |
| `typing.Supports*` | Work with static type checkers | Unreliable at runtime for complex numbers |
| `Union[float, Decimal, Fraction]` | Correct for static checking | Does not support external numeric types |

**Current recommendation:** Use `typing.Supports*` protocols for static checking. Use `numbers` ABCs only for runtime checking if you don't plan to use static type checkers.

## See Also

- [[typing-map-four-approaches]] -- static duck typing in the typing map
- [[typing-map-four-approaches]] -- how to design good protocols
- [[dynamic-protocols-and-duck-typing]] -- the informal predecessor
- [[goose-typing-and-abcs]] -- the runtime alternative
