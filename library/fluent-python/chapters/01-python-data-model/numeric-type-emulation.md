---
title: "Emulating Numeric Types: Vector"
book: "Fluent Python"
chapter: 1
tags: [python, data-model, operator-overloading, vector, numeric, add, mul, abs]
related:
  - "[[special-dunder-methods]]"
  - "[[string-representation]]"
  - "[[boolean-value-custom-types]]"
---

## Summary

The `Vector` class from Chapter 1 demonstrates how to make custom objects respond to arithmetic operators and built-in math functions. By implementing `__add__`, `__mul__`, `__abs__`, `__repr__`, and `__bool__`, a simple 2D vector class supports `+`, `*`, `abs()`, and boolean testing -- behaving like a first-class numeric type.

## How It Works

Here is the complete Vector class:

```python
import math

class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Vector({self.x!r}, {self.y!r})'

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector(x, y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
```

Each special method maps to a built-in function or operator:

| Expression | Special method called |
|-----------|---------------------|
| `v1 + v2` | `v1.__add__(v2)` |
| `v * 3` | `v.__mul__(3)` |
| `abs(v)` | `v.__abs__()` |
| `bool(v)` | `v.__bool__()` |
| `repr(v)` | `v.__repr__()` |

### Immutability of Operators

A critical design principle: `__add__` and `__mul__` return **new** Vector instances. They never modify `self` or `other`. This is the expected behavior for infix operators -- just as `3 + 4` does not change `3`, `v1 + v2` should not change `v1`.

```python
v1 = Vector(2, 4)
v2 = Vector(2, 1)
v3 = v1 + v2       # v3 is Vector(4, 5); v1 and v2 are unchanged
```

### The `__abs__` Method

`abs()` is a built-in that returns the absolute value of numbers and the magnitude of complex numbers. For consistency, Vector uses `abs()` to return the Euclidean magnitude (length) of the vector. `math.hypot(x, y)` computes `sqrt(x**2 + y**2)` efficiently.

### Boolean from Magnitude

`__bool__` converts the vector to a boolean. A zero-magnitude vector (the origin) is falsy; any other vector is truthy. The implementation `bool(abs(self))` chains `__abs__` to get the magnitude, then converts to bool (`0.0` is falsy, any nonzero float is truthy).

A faster alternative avoids the square root:
```python
def __bool__(self):
    return bool(self.x or self.y)
```

This works because `or` returns the first truthy operand (or the last operand if all are falsy), and any nonzero number is truthy.

## In Practice

Operator overloading is used extensively in Python's scientific ecosystem:

- **NumPy** arrays support `+`, `-`, `*`, `/`, `@` (matrix multiply) and broadcasting via special methods.
- **Pandas** DataFrames and Series support arithmetic operators element-wise.
- The `decimal.Decimal` and `fractions.Fraction` standard library types use the same mechanism.
- **SymPy** uses operator overloading for symbolic mathematics.

When designing your own numeric types, follow these conventions:
- `__add__` and `__mul__` should return new instances (never mutate).
- Use `__iadd__` and `__imul__` for in-place versions (`+=`, `*=`), typically only for mutable types.
- Return `NotImplemented` (not raise `NotImplementedError`) when an operand type is not supported, so Python can try the reflected method.

## Common Pitfalls

1. **`v * 3` works but `3 * v` does not.** The current implementation only handles `Vector.__mul__(scalar)`. For `3 * v`, Python first tries `int.__mul__(3, v)`, which returns `NotImplemented`, then looks for `Vector.__rmul__(3)`. Without `__rmul__`, you get `TypeError`. The fix (covered in Chapter 16):
   ```python
   def __rmul__(self, scalar):
       return self * scalar
   ```

2. **No type checking on `other`.** The simple `__add__` accesses `other.x` and `other.y` without checking whether `other` is actually a Vector. With a string or list, you get `AttributeError`. Robust implementations should return `NotImplemented` for unsupported types.

3. **Confusing `__abs__` with `__neg__`.** `abs()` returns the magnitude (a scalar). `__neg__` implements the unary `-` operator (`-v`), returning a new Vector pointing in the opposite direction.

4. **Mutable operator results.** If you accidentally return `self` from `__add__` instead of a new instance, modifying the result will also modify the original. Always create a new object.

5. **Forgetting `__repr__`.** Without it, your Vector displays as `<Vector object at 0x...>` -- useless for debugging. `__repr__` should ideally produce output that looks like a valid constructor call.

## See Also

- [[special-dunder-methods]] -- The full framework behind operator overloading
- [[string-representation]] -- Details on the `__repr__` used in Vector
- [[boolean-value-custom-types]] -- How `__bool__` makes vectors truthy/falsy
