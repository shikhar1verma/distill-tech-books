---
title: "Unary Operators: __neg__, __pos__, __abs__, __invert__"
book: "Fluent Python"
chapter: 16
tags: [python, operator-overloading, unary-operators, dunder-methods, data-model]
related:
  - "[[overloading-add-and-radd]]"
  - "[[operator-overloading-rules]]"
  - "[[special-dunder-methods]]"
---

# Unary Operators: `__neg__`, `__pos__`, `__abs__`, `__invert__`

> **One-sentence summary.** Unary operators `-`, `+`, `~`, and `abs()` are implemented via `__neg__`, `__pos__`, `__invert__`, and `__abs__` respectively, and each must return a new object without mutating `self`.

## How It Works

Python defines four unary operator special methods. When you write `-x`, Python calls `x.__neg__()`. When you write `abs(x)`, Python calls `x.__abs__()`. The mapping is straightforward:

| Operator | Special Method | Description |
|----------|---------------|-------------|
| `-x` | `__neg__` | Arithmetic negation |
| `+x` | `__pos__` | Arithmetic unary plus |
| `~x` | `__invert__` | Bitwise NOT (`~x == -(x+1)` for integers) |
| `abs(x)` | `__abs__` | Absolute value |

The fundamental contract: **always return a new object**. Never modify `self`. For `-` and `+`, the result is typically an instance of the same class. For `abs()`, the result is usually a scalar number. For `~`, the result depends on the domain -- for integers it is the bitwise inverse, for pandas it negates boolean filters.

```python
import math
from array import array


class Vector:
    typecode = 'd'

    def __init__(self, components):
        self._components = array(self.typecode, components)

    def __iter__(self):
        return iter(self._components)

    def __repr__(self):
        return f'Vector([{", ".join(repr(c) for c in self._components)}])'

    def __abs__(self):
        return math.hypot(*self)

    def __neg__(self):
        return Vector(-x for x in self)  # new Vector with negated components

    def __pos__(self):
        return Vector(self)  # new Vector copying self's components
```

The `__neg__` implementation builds a new `Vector` from a generator expression that negates each component. The `__pos__` implementation builds a new `Vector` from `self`, which works because `Vector` is iterable and its constructor accepts any iterable. Neither method touches the original object.

If you do not implement a unary operator, Python raises `TypeError` with a clear message. For example, if `__invert__` is not defined and the user tries `~v`, the error says `bad operand type for unary ~: 'Vector'`.

## When `x != +x`

In almost all cases, `x == +x` is `True`. However, the Python standard library has two notable exceptions.

### `decimal.Decimal` with changed context precision

When you create a `Decimal` value in one arithmetic context and then apply `+` in a different context, the result reflects the new precision:

```python
import decimal

ctx = decimal.getcontext()
ctx.prec = 40
one_third = decimal.Decimal('1') / decimal.Decimal('3')
# one_third has 40 digits of precision

ctx.prec = 28
assert one_third != +one_third  # +one_third has only 28 digits
```

This happens because `__pos__` creates a new `Decimal` using the current arithmetic context. The original retains its 40-digit precision, but the new one is computed with 28-digit precision.

### `collections.Counter` with negative tallies

The `Counter` class uses `+` as a shortcut for adding an empty `Counter`, which filters out zero and negative tallies:

```python
from collections import Counter

ct = Counter('abracadabra')
ct['r'] = -3
ct['d'] = 0
# +ct drops entries with count <= 0
assert +ct == Counter({'a': 5, 'b': 2, 'c': 1})
```

This is by design -- `Counter` arithmetic discards non-positive tallies from results for practical reasons.

## In Practice

Unary operators are the simplest form of operator overloading. The implementation pattern is always the same:

1. Accept only `self` as an argument.
2. Compute the result using whatever logic makes sense for the domain.
3. Return a **new** instance.

For immutable types, `__pos__` can return `self` directly (since it cannot be mutated, there is no need to copy). For mutable types, `__pos__` should return a copy. In the `Vector` example, the class is effectively immutable (the internal `array` is not exposed), so returning a copy is a safe convention either way.

Most user-defined classes only need `__neg__` and `__abs__`. Implementing `__pos__` is rarely necessary unless your domain has a meaningful interpretation of unary `+`. Implementing `__invert__` only makes sense if your type represents bitwise data or boolean masks.

## Connection to Other Concepts

Unary operators are the entry point for operator overloading in Python. Once you understand the "return a new object" contract, you are ready for infix operators (`__add__`, `__mul__`, `__matmul__`) which follow the same principle but add the complexity of dealing with two operands and the forward/reverse dispatch protocol. The rules governing all operator overloading are covered in [[operator-overloading-rules]].
