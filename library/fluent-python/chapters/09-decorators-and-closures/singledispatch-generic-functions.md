---
title: "Single Dispatch Generic Functions"
slug: singledispatch-generic-functions
chapter: 9
book: "Fluent Python"
type: code-heavy
depends_on:
  - implementing-decorators
tags:
  - singledispatch
  - generic-functions
  - polymorphism
  - functools
  - python
---

# Single Dispatch Generic Functions

## The Problem

You want a function that behaves differently based on the type of its first argument, but without writing a long `if/elif` chain:

```python
# Bad: tightly coupled, not extensible
def htmlize(obj):
    if isinstance(obj, str):
        ...
    elif isinstance(obj, int):
        ...
    elif isinstance(obj, list):
        ...
```

## The Solution: @singledispatch

`functools.singledispatch` turns a function into a **generic function** that dispatches on the type of its first argument.

```python
from functools import singledispatch

@singledispatch
def htmlize(obj: object) -> str:
    """Base implementation: handles any type not specifically registered."""
    content = html.escape(repr(obj))
    return f'<pre>{content}</pre>'
```

### Registering Specialized Implementations

Use `@htmlize.register` with a type hint on the first parameter:

```python
@htmlize.register
def _(text: str) -> str:
    content = html.escape(text).replace('\n', '<br/>\n')
    return f'<p>{content}</p>'

@htmlize.register
def _(n: numbers.Integral) -> str:
    return f'<pre>{n} (0x{n:x})</pre>'
```

The function name does not matter -- `_` is conventional since these are never called directly.

### Alternative: Explicit Type Argument

For Python 3.4+ compatibility, or when you prefer not to use type hints:

```python
@htmlize.register(fractions.Fraction)
def _(x) -> str:
    frac = fractions.Fraction(x)
    return f'<pre>{frac.numerator}/{frac.denominator}</pre>'
```

### Stacking for Multiple Types

```python
@htmlize.register(decimal.Decimal)
@htmlize.register(float)
def _(x) -> str:
    frac = fractions.Fraction(x).limit_denominator()
    return f'<pre>{x} ({frac.numerator}/{frac.denominator})</pre>'
```

## Dispatch Resolution

`singledispatch` selects the **most specific** matching type, regardless of registration order. For example, `bool` is a subtype of `int` (which is `numbers.Integral`), so a registered `bool` handler takes priority over the `numbers.Integral` handler.

## Best Practices

- **Register on ABCs** (`numbers.Integral`, `abc.Sequence`) rather than concrete types (`int`, `list`). This supports a wider range of compatible types.
- **Keep it modular.** Specialized handlers can be registered in different modules -- the system is designed for extensibility.
- **Single dispatch only.** Dispatch is based on the first argument only. For multiple-argument dispatch, look at third-party libraries like `multipledispatch`.

## Key Advantages Over if/elif

| Feature | if/elif | singledispatch |
|---|---|---|
| Extensible by other modules | No | Yes |
| Supports third-party types | Awkward | Easy |
| Dispatch on ABCs | Manual isinstance | Automatic |
| Code organization | Monolithic | Modular |

## See Also

- [[implementing-decorators]] -- singledispatch itself is a decorator
- [[parameterized-decorators]] -- `@htmlize.register(type)` is a parameterized decorator
