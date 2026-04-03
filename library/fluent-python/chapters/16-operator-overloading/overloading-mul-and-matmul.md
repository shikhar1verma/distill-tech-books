---
title: "Overloading * and @ for Scalar and Matrix Multiplication"
book: "Fluent Python"
chapter: 16
tags: [python, operator-overloading, __mul__, __matmul__, duck-typing, goose-typing, PEP-465]
related:
  - "[[overloading-add-and-radd]]"
  - "[[operator-overloading-rules]]"
  - "[[goose-typing-and-abcs]]"
---

# Overloading `*` and `@` for Scalar and Matrix Multiplication

> **One-sentence summary.** `__mul__`/`__rmul__` handle scalar multiplication using duck typing (try `float(scalar)`, return `NotImplemented` on failure), while `__matmul__`/`__rmatmul__` implement the `@` dot-product operator (PEP 465, Python 3.5+) using goose typing with `abc.Sized` and `abc.Iterable` isinstance checks.

## Scalar Multiplication with `__mul__` / `__rmul__`

Scalar multiplication means multiplying every component of a vector by a single number. The scalar can be any type convertible to `float`: `int`, `bool`, `Fraction`, or any custom numeric type. The implementation uses **duck typing** -- rather than checking the type of the scalar, we try to convert it:

```python
class Vector:
    def __mul__(self, scalar):
        try:
            factor = float(scalar)
        except TypeError:
            return NotImplemented
        return Vector(n * factor for n in self)

    def __rmul__(self, scalar):
        return self * scalar  # delegates to __mul__
```

The logic is simple:

1. Try `float(scalar)`. If the scalar is an `int`, `bool`, `Fraction`, or anything that defines `__float__`, this succeeds.
2. If the conversion raises `TypeError` (e.g., the scalar is a `str` or a `list`), return `NotImplemented` to give the other operand a chance.
3. Build a new `Vector` with each component multiplied by the factor.

Since scalar multiplication is commutative (`v * 3 == 3 * v`), `__rmul__` simply delegates to `__mul__`. This handles expressions like `11 * v1` where the left operand is a plain `int`.

### What the duck typing approach accepts

```python
v = Vector([1, 2, 3])
v * 10            # int -> float(10) = 10.0
v * True          # bool -> float(True) = 1.0
v * Fraction(1,3) # Fraction -> float(Fraction(1,3)) = 0.333...
```

What it rejects (returns `NotImplemented`, eventually raising `TypeError`):

```python
v * 'abc'         # float('abc') -> ValueError, but caught
v * [1, 2]        # float([1,2]) -> TypeError -> NotImplemented
```

Note: `complex` numbers cannot be converted to `float`, so `v * (1+2j)` will also fail. This is intentional because our `Vector` uses a `float` array internally.

### Duck typing vs. goose typing for `__mul__`

In the first edition of Fluent Python, Ramalho used goose typing: `isinstance(scalar, numbers.Real)`. In the second edition, he switched to duck typing because the `numbers` ABCs are not supported by PEP 484 static typing. Using types at runtime that cannot be statically checked seemed like a bad trade-off.

## Matrix Multiplication with `__matmul__` / `__rmatmul__` (the `@` operator)

The `@` operator was added in Python 3.5 via PEP 465 to give matrix multiplication a dedicated infix symbol. Before this, NumPy users wrote `numpy.dot(a, b)`, which made complex mathematical expressions hard to read.

For our `Vector` class, `@` computes the dot product: the sum of pairwise products of corresponding components.

```python
from collections import abc

class Vector:
    def __matmul__(self, other):
        if (isinstance(other, abc.Sized) and
                isinstance(other, abc.Iterable)):
            if len(self) == len(other):
                return sum(a * b for a, b in zip(self, other))
            else:
                raise ValueError('@ requires vectors of equal length.')
        return NotImplemented

    def __rmatmul__(self, other):
        return self @ other
```

This implementation uses **goose typing** rather than duck typing. The isinstance checks against `abc.Sized` and `abc.Iterable` verify that the other operand supports both `len()` and iteration, without requiring it to be a specific type.

### Why goose typing here?

If we used duck typing (just trying the operation), an `int` or `float` operand would raise confusing errors deep in the `zip`/`sum` chain. By checking upfront that `other` is both sized and iterable, we can return `NotImplemented` immediately for scalars, producing a clean `TypeError` message.

The goose typing approach is also more flexible than checking `isinstance(other, Vector)`. Any object that implements `__len__` and `__iter__` qualifies -- including plain `list`, `tuple`, `array.array`, and NumPy arrays. The `abc.Sized` and `abc.Iterable` ABCs both implement `__subclasshook__`, so objects pass the isinstance check purely by having the right methods, without needing to subclass or register.

```python
va = Vector([1, 2, 3])
vb = Vector([5, 6, 7])
va @ vb                    # 1*5 + 2*6 + 3*7 = 38.0
[10, 20, 30] @ vb          # works! list is Sized and Iterable
```

### Equal-length requirement

Unlike `__add__` which pads shorter vectors with zeros, `__matmul__` raises `ValueError` when vectors have different lengths. A dot product is only defined for vectors of equal dimension. In Python 3.10+, you could use `zip(self, other, strict=True)` to enforce this automatically.

## Duck Typing vs. Goose Typing: When to Use Which

The chapter demonstrates both strategies in the same class:

| Method | Strategy | Rationale |
|--------|----------|-----------|
| `__mul__` | Duck typing | The scalar is a single value; `float()` conversion is the natural validity test |
| `__matmul__` | Goose typing | The operand is a collection; checking `Sized` and `Iterable` prevents confusing errors from deep in iterator chains |

The general guidance: use duck typing when a simple conversion or operation naturally validates the input. Use goose typing (isinstance against ABCs) when you need structural guarantees (like "this thing has a length and can be iterated") before proceeding with a complex computation.

## Connection to Other Concepts

The `__mul__`/`__rmul__` pattern is identical to `__add__`/`__radd__` (see [[overloading-add-and-radd]]). The key addition here is seeing two different type-checking strategies applied in the same class. The goose typing used in `__matmul__` connects directly to the ABC concepts from Chapter 13 (see [[goose-typing-and-abcs]]). Both operators follow Python's operator overloading rules (see [[operator-overloading-rules]]).
