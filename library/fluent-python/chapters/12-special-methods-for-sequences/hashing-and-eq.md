---
title: "Hashing and a Faster ==: __hash__ with reduce, __eq__ with zip"
book: "Fluent Python"
chapter: 12
tags: [python, __hash__, __eq__, functools-reduce, operator-xor, map-reduce, zip, hashable]
type: "code-heavy"
depends_on:
  - "[[vector-multidimensional-sequence]]"
  - "[[protocols-and-duck-typing]]"
related:
  - "[[formatting-with-format]]"
  - "[[dynamic-attribute-access]]"
  - "[[hashability]]"
---

## Summary

Making `Vector` hashable requires implementing both `__hash__` and `__eq__`. The hash is computed via a **map-reduce** pattern: map each component to its `hash()` value, then reduce all those hashes with XOR (`^`) using `functools.reduce(operator.xor, ...)`. The `__eq__` method is optimized from the naive tuple-comparison approach to a length check followed by `zip` + `all`, which short-circuits on the first mismatched component without allocating any intermediate data structures.

## The Map-Reduce Hash

### Why XOR?

The `Vector2d` class from Chapter 11 hashed by building a tuple of its two components and hashing that. For a `Vector` with thousands of components, constructing a temporary tuple is wasteful. Instead, we XOR individual hashes together:

```python
v[0].__hash__() ^ v[1].__hash__() ^ v[2].__hash__() ^ ...
```

XOR is chosen because it is:
- **Commutative and associative**: Order of operations does not matter for correctness.
- **Fast**: A single CPU instruction.
- **Appropriate for hash combining**: The identity value is 0 (`x ^ 0 == x`).

### Understanding `functools.reduce`

`reduce(fn, iterable, initializer)` applies a two-argument function cumulatively:

```python
reduce(fn, [a, b, c, d], init)
# computes: fn(fn(fn(fn(init, a), b), c), d)
```

Three ways to compute the aggregate XOR of 0 through 5:

```python
# 1. Explicit loop
n = 0
for i in range(1, 6):
    n ^= i
# n == 1

# 2. reduce with lambda
functools.reduce(lambda a, b: a ^ b, range(6))
# == 1

# 3. reduce with operator.xor (preferred)
functools.reduce(operator.xor, range(6))
# == 1
```

The `operator` module provides function versions of all Python operators, eliminating the need for lambdas. `operator.xor` is clearer and slightly faster than `lambda a, b: a ^ b`.

### The Implementation

```python
def __hash__(self):
    hashes = (hash(x) for x in self)              # map step (generator)
    return functools.reduce(operator.xor, hashes, 0)  # reduce step
```

**Map step**: A generator expression lazily computes `hash(x)` for each component. No intermediate list is created.

**Reduce step**: `functools.reduce` combines all hashes with XOR. The third argument `0` is the initializer -- crucial for empty vectors, which would otherwise raise `TypeError: reduce() of empty sequence with no initial value`.

An equivalent implementation using `map()`:

```python
def __hash__(self):
    hashes = map(hash, self._components)
    return functools.reduce(operator.xor, hashes, 0)
```

Both are equally efficient in Python 3, where `map` returns a lazy iterator.

### The Initializer Rule

Always provide an initializer to `reduce`. The initializer should be the **identity value** for the operation:

| Operation | Identity | Reason |
|-----------|----------|--------|
| `+` | `0` | `x + 0 == x` |
| `*` | `1` | `x * 1 == x` |
| `^` (XOR) | `0` | `x ^ 0 == x` |
| `\|` (OR) | `0` | `x \| 0 == x` |
| `&` (AND) | `~0` (-1) | `x & ~0 == x` |

## The Efficient `__eq__`

### The Problem with Tuples

The baseline `__eq__` was:

```python
def __eq__(self, other):
    return tuple(self) == tuple(other)
```

This builds two complete tuples in memory before comparing. For vectors with 10,000 components, that means 10,000 Python float objects created, compared, and discarded. Even worse, if the vectors differ only in the first component, all that work is wasted.

### The `zip` + `all` Solution

```python
def __eq__(self, other):
    return (len(self) == len(other) and
            all(a == b for a, b in zip(self, other)))
```

1. **Length check first**: `zip` stops at the shorter iterable *without warning*. Without the length check, `Vector([1, 2, 3])` would equal `Vector([1, 2, 3, 4])`. This is the most common `zip` pitfall.

2. **`zip` produces pairs lazily**: No intermediate tuple or list is created.

3. **`all` short-circuits**: As soon as one pair differs (`a != b`), `all` returns `False` immediately. For vectors that differ in the first component, this is O(1) instead of O(n).

### The Explicit Loop Equivalent

For clarity, here is what `zip` + `all` replaces:

```python
def __eq__(self, other):
    if len(self) != len(other):
        return False
    for a, b in zip(self, other):
        if a != b:
            return False
    return True
```

The `all` version is a one-liner with identical semantics and performance.

## `__hash__` and `__eq__` Must Be Consistent

Python requires that objects which compare equal have the same hash:

```
if a == b, then hash(a) == hash(b)
```

The reverse is not required (hash collisions are normal). This is why `__hash__` and `__eq__` should always be implemented together and kept close in source code.

Our XOR-based hash satisfies this: if two vectors have the same components in the same order, their element-wise hashes are identical, and XOR over identical sequences yields identical results.

## In Practice

Once `Vector` is hashable, it can serve as a dictionary key or set member:

```python
v1 = Vector([3, 4])
v2 = Vector([3.1, 4.2])
d = {v1: '2D integer', v2: '2D float'}
print(d[Vector([3, 4])])  # '2D integer' -- lookup by value
```

This enables patterns like caching computed properties indexed by vector values, or deduplicating vectors in a set.

## Gotchas

- **Mutable objects should not be hashable**: If components could change after hashing, the hash would become stale and the object would be "lost" in dicts/sets. `Vector` is safe because we blocked component writes in `__setattr__`.
- **`zip` stops silently**: Without the `len` guard, vectors of different lengths could compare as equal. Python 3.10 added `zip(strict=True)` which raises `ValueError` on length mismatch, but using it here would be wrong -- we want to return `False`, not raise.
- **Empty vector hash is 0**: `reduce(operator.xor, (), 0)` returns 0. This is fine -- `hash(0)` and `hash(0.0)` are both 0 in CPython, so empty vectors hash like zero, which is a reasonable convention.
- **`Vector([1, 2]) == (1, 2)` is `True`**: The `__eq__` implementation compares against any iterable with matching length and values. This may be undesirable and is addressed in Chapter 16 with operator overloading.

## See Also

- [[vector-multidimensional-sequence]] -- The class this version extends
- [[hashability]] -- Chapter 3's discussion of what makes an object hashable
- [[formatting-with-format]] -- The final enhancement to Vector
- [[dynamic-attribute-access]] -- The previous step: `__getattr__` and `__setattr__`
