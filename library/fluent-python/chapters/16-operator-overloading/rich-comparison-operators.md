---
title: "Rich Comparison Operators"
book: "Fluent Python"
chapter: 16
tags: [python, operator-overloading, comparison, __eq__, __lt__, total_ordering]
related:
  - "[[overloading-add-and-radd]]"
  - "[[operator-overloading-rules]]"
  - "[[special-dunder-methods]]"
---

# Rich Comparison Operators

> **One-sentence summary.** `==` and `!=` have special fallback behavior -- `==` falls back to identity comparison (`id`), `!=` negates `==` -- while ordering operators (`>`, `<`, `>=`, `<=`) raise `TypeError` if both sides return `NotImplemented`; the reverse of `__gt__` is `__lt__` (not `__rgt__`); and `functools.total_ordering` can auto-generate missing comparison methods.

## How It Works

Rich comparison operators follow a dispatch protocol similar to arithmetic operators but with two important differences.

### Difference 1: Reverse methods are the "mirror" operators

Arithmetic operators have distinct `__r*__` methods (`__radd__`, `__rsub__`, etc.). Comparison operators do not. Instead, the "reverse" of a comparison is its mirror:

| Expression | Forward call | Reverse call | Fallback |
|-----------|-------------|-------------|----------|
| `a == b` | `a.__eq__(b)` | `b.__eq__(a)` | `id(a) == id(b)` |
| `a != b` | `a.__ne__(b)` | `b.__ne__(a)` | `not (a == b)` |
| `a > b` | `a.__gt__(b)` | `b.__lt__(a)` | Raise `TypeError` |
| `a < b` | `a.__lt__(b)` | `b.__gt__(a)` | Raise `TypeError` |
| `a >= b` | `a.__ge__(b)` | `b.__le__(a)` | Raise `TypeError` |
| `a <= b` | `a.__le__(b)` | `b.__ge__(a)` | Raise `TypeError` |

Notice: the reverse of `__gt__` is `__lt__`, not `__rgt__`. The interpreter swaps both the operands and the direction of the comparison.

### Difference 2: Fallback behavior for `==` and `!=`

For `==`, if both the forward and reverse calls return `NotImplemented`, Python does **not** raise `TypeError`. Instead, it falls back to comparing object identity: `id(a) == id(b)`. This means `==` always produces a boolean result (it never raises an error for incompatible types).

For `!=`, the fallback is `not (a == b)`. Since `object.__ne__` is defined as the negation of `__eq__`, you almost never need to implement `__ne__` yourself.

For ordering operators (`>`, `<`, `>=`, `<=`), if both sides return `NotImplemented`, Python raises `TypeError`. This makes sense: there is no reasonable default for ordering objects of incompatible types.

## Implementation

### Basic `__eq__` with type checking

```python
class Vector:
    def __eq__(self, other):
        if isinstance(other, Vector):
            return (len(self) == len(other) and
                    all(a == b for a, b in zip(self, other)))
        return NotImplemented
```

This is more conservative than checking any iterable. Returning `NotImplemented` for non-Vector types lets Python try the other operand's `__eq__`. The step-by-step evaluation of `Vector([1,2,3]) == (1,2,3)`:

1. Python calls `Vector.__eq__(va, (1,2,3))`.
2. `(1,2,3)` is not a `Vector`, so return `NotImplemented`.
3. Python tries `tuple.__eq__((1,2,3), va)`.
4. `tuple.__eq__` does not know about `Vector`, returns `NotImplemented`.
5. As the `==` fallback, Python compares `id(va) == id((1,2,3))` -- `False`.

Without the isinstance check, `Vector([1,2,3]) == (1,2,3)` would return `True` because both are iterables with the same elements. Whether this is desirable depends on the application, but the book follows Python's own convention: `[1,2] == (1,2)` is `False`.

### You get `__ne__` for free

The `__ne__` inherited from `object` works like this:

```python
def __ne__(self, other):
    eq_result = self == other
    if eq_result is NotImplemented:
        return NotImplemented
    return not eq_result
```

If your `__eq__` is correct, `__ne__` works automatically. There is no need to implement it.

### Cross-type equality via reverse dispatch

Even without explicit cross-type support, the dispatch protocol can make it work:

```python
vc = Vector([1, 2])
v2d = Vector2d(1, 2)
vc == v2d  # True!
```

How? `Vector.__eq__` returns `NotImplemented` (v2d is not a Vector). Python then calls `Vector2d.__eq__(v2d, vc)`, which converts both to tuples and compares. The result is `True`.

## `functools.total_ordering`

If you need all six comparison operators but only want to write two, use the `@total_ordering` decorator. You define `__eq__` and one ordering method (typically `__lt__`), and the decorator generates the rest:

```python
from functools import total_ordering

@total_ordering
class Temperature:
    def __init__(self, value):
        self.value = float(value)

    def __eq__(self, other):
        if isinstance(other, Temperature):
            return self.value == other.value
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Temperature):
            return self.value < other.value
        return NotImplemented
```

With just `__eq__` and `__lt__`, `total_ordering` synthesizes `__gt__`, `__ge__`, and `__le__`. The generated methods handle `NotImplemented` correctly.

Caveat: the generated methods are slightly slower than hand-written ones because they are built from combinations of `__eq__` and `__lt__`. For performance-critical code with millions of comparisons, consider implementing all six manually.

## In Practice

The most important practical lessons:

1. **Always return `NotImplemented`** from `__eq__` for unrecognized types, rather than returning `False`. Returning `False` directly prevents the other operand from handling the comparison.

2. **Be conservative with equality.** Following Python's own convention (`[1,2] != (1,2)`), it is usually better to restrict equality to instances of the same type (or its subclasses). Use isinstance checks.

3. **Skip `__ne__`.** The inherited version works correctly in virtually all cases.

4. **Use `@total_ordering`** when you need ordering. It saves boilerplate and reduces the chance of inconsistencies between comparison methods.

5. **Ordering operators should raise `TypeError`** (via `NotImplemented` return) for incompatible types. Do not return `False` -- that creates confusing situations where `a < b` is `False` and `a >= b` is also `False`.

## Connection to Other Concepts

Rich comparison operators use the same `NotImplemented` protocol as arithmetic operators (see [[overloading-add-and-radd]]), but with different reverse dispatch rules and fallback behavior. The isinstance-based type checking connects to the broader discussion of duck typing vs. goose typing in operator overloading (see [[overloading-mul-and-matmul]]). The overall rules governing all operator overloading are in [[operator-overloading-rules]].
