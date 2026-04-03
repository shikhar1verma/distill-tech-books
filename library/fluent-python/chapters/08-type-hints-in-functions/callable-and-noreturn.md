---
title: "Callable, NoReturn, and Variadic Annotations"
book: "Fluent Python"
chapter: 8
tags: [python, type-hints, Callable, NoReturn, variance, callbacks, variadic]
related:
  - "[[gradual-typing-and-mypy]]"
  - "[[any-optional-union]]"
  - "[[static-protocols]]"
---

# Callable, NoReturn, and Variadic Annotations

`Callable[[ParamTypes], ReturnType]` annotates callback parameters and callable objects with precise type information, including variance rules that govern substitutability. `NoReturn` marks functions that always raise exceptions and never return normally. Variadic parameter annotations (`*args: str`, `**kwargs: str`) describe the type of each individual argument.

## How It Works

### Callable Syntax

`Callable` takes two parameters in brackets: a list of parameter types, and the return type.

```python
from collections.abc import Callable

# A function that takes no args and returns float
probe: Callable[[], float]

# A function that takes a float and returns None
display: Callable[[float], None]

# A function that takes str and int, returns bool
validator: Callable[[str, int], bool]
```

For functions with flexible signatures (optional or keyword arguments), replace the parameter list with `...`:

```python
# Accepts any callable that returns str, regardless of parameters
formatter: Callable[..., str]
```

### Practical Example: Callbacks

```python
from collections.abc import Callable

def update(
    probe: Callable[[], float],
    display: Callable[[float], None]
) -> None:
    temperature = probe()
    display(temperature)

def my_probe() -> int:
    return 42

def my_display(temperature: complex) -> None:
    print(f"Temperature: {temperature}")

update(my_probe, my_display)  # Both are valid -- see variance rules below
```

### Variance in Callable Types

`Callable` has special variance rules that match real-world substitutability:

**Covariant in return type:** A callback returning `int` can substitute for one expected to return `float`, because `int` is consistent-with `float`. The return value "goes out" to the caller.

```python
# probe expects Callable[[], float] but my_probe returns int -- OK!
# Because: Callable[[], int] is subtype-of Callable[[], float]
def my_probe() -> int:
    return 42
```

**Contravariant in parameter types:** A callback accepting `complex` can substitute for one expected to accept `float`, because any `float` is also a valid `complex`. The parameter "comes in" from the caller.

```python
# display expects Callable[[float], None]
def display_ok(temperature: complex) -> None:   # OK: complex accepts float
    print(temperature)

def display_wrong(temperature: int) -> None:     # ERROR: int may not handle float
    print(hex(temperature))
```

The intuition: a more permissive function (accepts wider types) is safe to use where a less permissive one is expected.

### NoReturn

`NoReturn` annotates functions that never return -- they always raise an exception or run forever.

```python
from typing import NoReturn

def exit_program(status: str) -> NoReturn:
    raise SystemExit(status)

def infinite_loop() -> NoReturn:
    while True:
        pass
```

Common uses in the standard library:
- `sys.exit()` -- raises `SystemExit`
- `typing.assert_never()` -- for exhaustiveness checking

### Variadic Parameter Annotations

The type hint for `*args` describes the type of each individual positional argument, not the tuple itself:

```python
def tag(
    name: str,
    /,
    *content: str,          # Each arg is str; content: tuple[str, ...]
    class_: str | None = None,
    **attrs: str,           # Each value is str; attrs: dict[str, str]
) -> str:
    ...
```

| Annotation | Parameter type inside function |
|-----------|-------------------------------|
| `*args: str` | `args: tuple[str, ...]` |
| `**kwargs: int` | `kwargs: dict[str, int]` |
| `*args: Any` | `args: tuple[Any, ...]` |

Note: there is no syntax to annotate individual keyword arguments with different types in `**kwargs`. If you need heterogeneous keyword types, use `**kwargs: Any` or consider `TypedDict` with unpacking (Python 3.12+).

### Positional-Only Parameters

Python 3.8+ uses `/` to mark positional-only parameters:

```python
def tag(name: str, /, *content: str) -> str:
    ...
```

For older Python, PEP 484 uses a double-underscore prefix convention:

```python
def tag(__name: str, *content: str) -> str:
    ...
```

## In Practice

- **Use `Callable` for callback parameters** in higher-order functions. This documents the expected signature clearly.
- **Use `Callable[..., ReturnType]`** when you only care about the return type, not the parameter signature.
- **`NoReturn` is rare** -- only use it for functions that truly never return. Do not use it for functions that return `None`.
- **Variance rules are intuitive once internalized**: a callback is compatible if it can handle any input the caller might send (contravariant on params) and produces output the caller can use (covariant on return).
- **For complex callback signatures**, consider defining a `Protocol` with a `__call__` method instead of using `Callable` -- this supports optional parameters, keyword arguments, and overloads.

## Common Pitfalls

- **Confusing `NoReturn` with `None`**: A function that returns nothing has return type `None`. A function that never returns (always raises) has return type `NoReturn`.
- **Forgetting variance rules**: A callback accepting `int` is NOT compatible where `Callable[[float], None]` is expected, even though `int` is subtype-of `float`. The direction reverses for parameters.
- **Annotating `*args` as the tuple type**: Write `*args: str`, not `*args: tuple[str, ...]`. The annotation describes each individual argument.
- **Using `Callable` for methods**: `Callable` does not account for `self`. For annotating method types, use `Protocol` with `__call__`.
- **No syntax for optional callback params**: `Callable[[int, str], bool]` cannot express that the second parameter is optional. Use `Callable[..., bool]` or a `Protocol`.

## See Also

- [[gradual-typing-and-mypy]] -- The gradual type system that Callable operates within
- [[any-optional-union]] -- `Any` as the fallback for flexible callable signatures
- [[static-protocols]] -- Protocols can define `__call__` for complex callable signatures
- Chapter 15 of Fluent Python -- Variance explained in depth (covariant, contravariant, invariant)
- PEP 484 -- Type Hints
