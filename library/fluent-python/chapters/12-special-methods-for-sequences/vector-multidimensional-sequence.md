---
title: "Vector: A User-Defined Multidimensional Sequence"
book: "Fluent Python"
chapter: 12
tags: [python, vector, sequence, array, reprlib, immutable, composition]
type: "code-heavy"
depends_on: []
related:
  - "[[protocols-and-duck-typing]]"
  - "[[sliceable-sequence-getitem]]"
  - "[[dynamic-attribute-access]]"
  - "[[hashing-and-eq]]"
  - "[[formatting-with-format]]"
---

## Summary

Chapter 12 builds a multidimensional `Vector` class that serves as the vehicle for exploring sequence special methods throughout the chapter. This first version establishes a baseline: it accepts any iterable of numbers, stores them internally in a compact `array.array('d', ...)` of floats, and provides compatibility with the earlier two-dimensional `Vector2d` class from Chapter 11 -- minus the incompatible constructor signature. The class uses composition (wrapping an array) rather than inheritance, and employs `reprlib.repr` to produce safe, truncated representations for vectors with thousands of components.

## Design Decisions

### Constructor: Iterable In, Not Positional Args

Built-in Python sequence types (`list`, `tuple`, `array.array`) accept an iterable in their constructor. `Vector` follows this convention:

```python
Vector([3.1, 4.2])       # from list
Vector((3, 4, 5))         # from tuple
Vector(range(10))          # from range
```

This is a deliberate departure from `Vector2d(3, 4)`, which took positional arguments. The authors considered using `*args` to support both styles but rejected it -- following the convention of the built-in types is more Pythonic and avoids ambiguity.

### Internal Storage: `array.array`

The `_components` attribute is an `array.array` with typecode `'d'` (C double-precision float, 8 bytes each). This provides:

- **Memory efficiency**: An `array` of 1,000 floats uses roughly 8 KB; a `list` of 1,000 `float` objects uses roughly 28 KB (each Python float is a 28-byte object plus an 8-byte pointer in the list).
- **Type homogeneity**: All components are guaranteed to be floats, which simplifies comparisons and hashing.
- **Fast byte serialization**: `bytes(self._components)` yields the raw memory representation directly.

### Safe Representation with `reprlib`

For debugging, `repr()` must never explode. A `Vector` with 10,000 components should not dump all of them to the console. `reprlib.repr` automatically truncates long output with `'...'`:

```python
>>> Vector(range(10))
Vector([0.0, 1.0, 2.0, 3.0, 4.0, ...])
```

The implementation applies `reprlib.repr` to the internal array, then strips the `array('d',` prefix and trailing `)` to produce clean output that looks like a valid constructor call:

```python
def __repr__(self):
    components = reprlib.repr(self._components)
    components = components[components.find('['):-1]
    return f'Vector({components})'
```

An alternative approach -- `reprlib.repr(list(self._components))` -- would produce the same visual result but wastefully copies every element into a temporary list.

## How It Works

The complete baseline `Vector` class:

```python
from array import array
import reprlib
import math

class Vector:
    typecode = 'd'

    def __init__(self, components):
        self._components = array(self.typecode, components)

    def __iter__(self):
        return iter(self._components)

    def __repr__(self):
        components = reprlib.repr(self._components)
        components = components[components.find('['):-1]
        return f'Vector({components})'

    def __str__(self):
        return str(tuple(self))

    def __bytes__(self):
        return bytes([ord(self.typecode)]) + bytes(self._components)

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __abs__(self):
        return math.hypot(*self)

    def __bool__(self):
        return bool(abs(self))

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(memv)
```

Key points about each method:

- **`__iter__`** returns `iter(self._components)`, making Vector iterable. This is the foundation that `__str__`, `__eq__`, and `__abs__` all rely on.
- **`__abs__`** uses `math.hypot(*self)` (available since Python 3.8 for N-dimensional points) to compute the Euclidean magnitude.
- **`__eq__`** converts both operands to tuples for comparison. This is simple but inefficient for large vectors -- it gets replaced in a later version.
- **`frombytes`** passes the `memoryview` directly to the constructor without unpacking, since the constructor now accepts any iterable.

## Composition Over Inheritance

The authors explicitly chose not to subclass `Vector2d`. Two reasons:

1. **Incompatible constructors**: `Vector2d(3, 4)` vs `Vector([3, 4])`. Reconciling these with parameter tricks would add complexity for no real benefit.
2. **Standalone example**: `Vector` is designed to teach the sequence protocol independently, without an inheritance hierarchy obscuring the lesson.

This reflects a general Python design principle: prefer composition when the "is-a" relationship is not clear-cut.

## Gotchas

- **`__repr__` must never raise**: If your `__repr__` implementation encounters an error, catch it and produce fallback output. A broken `repr` makes debugging nearly impossible.
- **`__eq__` comparing tuples is fragile**: `Vector([1, 2]) == (1, 2)` evaluates to `True` in this version because both sides convert to tuples. This is addressed in Chapter 16 with operator overloading.
- **`__str__` shows all components**: Unlike `__repr__`, `__str__` produces `str(tuple(self))` without truncation. For very large vectors, this could be problematic.

## See Also

- [[protocols-and-duck-typing]] -- Why implementing the right methods is enough
- [[sliceable-sequence-getitem]] -- Adding `__len__` and `__getitem__` with slice support
- [[hashing-and-eq]] -- Replacing the naive `__eq__` with an efficient version
