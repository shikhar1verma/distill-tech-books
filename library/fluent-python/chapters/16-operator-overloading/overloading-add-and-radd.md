---
title: "Overloading + with __add__ and __radd__"
book: "Fluent Python"
chapter: 16
tags: [python, operator-overloading, __add__, __radd__, NotImplemented, dispatch]
related:
  - "[[unary-operators]]"
  - "[[overloading-mul-and-matmul]]"
  - "[[augmented-assignment-operators]]"
  - "[[operator-overloading-rules]]"
---

# Overloading `+` with `__add__` and `__radd__`

> **One-sentence summary.** For `a + b`, Python tries `a.__add__(b)` first; if that returns `NotImplemented`, it tries `b.__radd__(a)`, and if both fail, it raises `TypeError` -- so always return `NotImplemented` (not raise an exception) to give the other operand a chance.

## How It Works

When Python evaluates the expression `a + b`, it follows a specific dispatch protocol:

1. If `a` has `__add__`, call `a.__add__(b)`. If it returns anything other than `NotImplemented`, that is the result.
2. If `a` does not have `__add__`, or if `a.__add__(b)` returned `NotImplemented`, check if `b` has `__radd__`. If so, call `b.__radd__(a)`. If it returns anything other than `NotImplemented`, that is the result.
3. If both calls return `NotImplemented` (or the methods do not exist), raise `TypeError` with a message like `unsupported operand type(s) for +: 'X' and 'Y'`.

The `__radd__` method is the "reversed" (or "reflected") version of `__add__`. Its purpose is to handle the case where the left operand does not know how to add the right operand. This is essential for mixed-type operations.

### The `NotImplemented` singleton

`NotImplemented` is a special singleton value -- not an exception. It is fundamentally different from `NotImplementedError`:

- **`NotImplemented`** -- a value you **return** from an operator method to signal "I don't know how to handle this operand." The interpreter then tries the reverse method.
- **`NotImplementedError`** -- an exception you **raise** in abstract method stubs to signal "subclasses must implement this."

Confusing the two is a common bug. If you accidentally raise `NotImplementedError` inside `__add__`, the exception propagates immediately and Python never gets to try `__radd__` on the other operand.

## Implementation Pattern

Here is the canonical pattern for implementing `+` on a `Vector` class:

```python
import itertools

class Vector:
    def __add__(self, other):
        try:
            pairs = itertools.zip_longest(self, other, fillvalue=0.0)
            return Vector(a + b for a, b in pairs)
        except TypeError:
            return NotImplemented  # let the other side try

    def __radd__(self, other):
        return self + other  # delegates to __add__
```

Key design decisions:

1. **Duck typing with error handling.** Rather than checking the type of `other`, we try to use it as an iterable. If it fails (e.g., `other` is an `int` or a string whose elements cannot be added to floats), we catch `TypeError` and return `NotImplemented`.

2. **`zip_longest` for different lengths.** When vectors have different lengths, shorter ones are padded with `0.0` instead of raising an error. This is useful in domains like information retrieval.

3. **`__radd__` delegates to `__add__`.** Since addition is commutative for our vectors, `__radd__` simply calls `self + other`, which triggers `self.__add__(other)`. This is the simplest and most common pattern.

For truly commutative operators, you can even write:

```python
__radd__ = __add__
```

This assigns the same function object to both names.

## Why `__radd__` Is Necessary

Without `__radd__`, mixed-type operations fail when the `Vector` is on the right:

```python
v1 = Vector([3, 4, 5])
(10, 20, 30) + v1  # tuple.__add__ doesn't know about Vector -> TypeError
```

The `tuple.__add__` method only knows how to concatenate tuples. It returns `NotImplemented` when given a `Vector`. Without `Vector.__radd__`, Python has no fallback and raises `TypeError`. With `__radd__`, Python calls `v1.__radd__((10, 20, 30))`, which delegates to `v1.__add__((10, 20, 30))` and succeeds because tuples are iterable.

## When `__radd__` Cannot Simply Delegate

For non-commutative operations like subtraction, `__rsub__` needs different logic:

```python
def __sub__(self, other):
    try:
        pairs = itertools.zip_longest(self, other, fillvalue=0.0)
        return Vector(a - b for a, b in pairs)
    except TypeError:
        return NotImplemented

def __rsub__(self, other):
    # a - b != b - a, so we must compute other - self
    try:
        pairs = itertools.zip_longest(other, self, fillvalue=0.0)
        return Vector(a - b for a, b in pairs)
    except TypeError:
        return NotImplemented
```

The `__rsub__` method is called when the left operand's `__sub__` fails. In `b.__rsub__(a)`, we need to compute `a - b`, not `b - a`.

## Common Pitfalls

1. **Raising `TypeError` instead of returning `NotImplemented`.** If your `__add__` raises `TypeError` for unsupported types, the interpreter never tries `__radd__` on the other operand. Always catch `TypeError` and return `NotImplemented`.

2. **Returning `NotImplementedError` (the exception class).** This is truthy, so Python treats it as a valid result rather than a signal to try the reverse method.

3. **Mutating operands.** Infix operators must never modify `self` or `other`. Always return a new object.

## Connection to Other Concepts

The `__add__`/`__radd__` pattern is the template for all infix arithmetic operators: `__mul__`/`__rmul__`, `__matmul__`/`__rmatmul__`, `__sub__`/`__rsub__`, and so on. The same dispatch protocol applies to every one of them. Rich comparison operators use a slightly different mechanism (see [[rich-comparison-operators]]), and augmented assignment operators like `__iadd__` add in-place mutation semantics (see [[augmented-assignment-operators]]).
