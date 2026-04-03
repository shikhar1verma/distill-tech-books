---
title: "A Sliceable Sequence: __getitem__ with Slice Support"
book: "Fluent Python"
chapter: 12
tags: [python, __getitem__, slice, operator-index, sequence-protocol, duck-typing]
type: "code-heavy"
depends_on:
  - "[[vector-multidimensional-sequence]]"
  - "[[protocols-and-duck-typing]]"
related:
  - "[[dynamic-attribute-access]]"
  - "[[hashing-and-eq]]"
  - "[[slicing]]"
---

## Summary

When Python evaluates `my_seq[1:4]`, it constructs a `slice(1, 4, None)` object and passes it to `my_seq.__getitem__`. A naive `__getitem__` that delegates directly to an internal list or array returns the container's own type (a raw `array` or `list`), not a new instance of your class. A Pythonic sequence must detect slice arguments and return a new instance of the same class. For integer keys, `operator.index()` is preferred over `int()` because it correctly rejects floats -- a float should never be used as an index.

## How Slicing Works Under the Hood

Python's slice syntax is pure syntactic sugar. The interpreter converts it into a `slice` object:

```python
class MySeq:
    def __getitem__(self, index):
        return index

s = MySeq()
s[1]         # -> 1
s[1:4]       # -> slice(1, 4, None)
s[1:4:2]     # -> slice(1, 4, 2)
s[1:4, 9]    # -> (slice(1, 4, None), 9)   -- a tuple!
```

The `slice` object has three attributes -- `start`, `stop`, `step` -- and an `indices(length)` method that normalizes negative or out-of-bounds values for a sequence of the given length:

```python
>>> slice(None, 10, 2).indices(5)
(0, 5, 2)    # 'ABCDE'[:10:2] == 'ABCDE'[0:5:2]
>>> slice(-3, None, None).indices(5)
(2, 5, 1)    # 'ABCDE'[-3:] == 'ABCDE'[2:5:1]
```

When your `__getitem__` delegates to an underlying sequence that already handles slices (like `array` or `list`), you can pass the `slice` object directly -- no need to call `indices()` yourself.

## The Implementation

The key idea is a two-branch `__getitem__`:

```python
import operator

def __len__(self):
    return len(self._components)

def __getitem__(self, key):
    if isinstance(key, slice):
        cls = type(self)
        return cls(self._components[key])  # new Vector from sliced array
    index = operator.index(key)
    return self._components[index]         # single float
```

### Branch 1: Slice

When `key` is a `slice`, we:
1. Get the class via `type(self)` (not hardcoding `Vector`) so subclasses work correctly.
2. Slice the internal `_components` array, which returns a new `array`.
3. Pass that array to the class constructor, producing a new `Vector`.

This follows a universal Python convention: **slicing a sequence produces a new instance of the same type**. `list[1:3]` returns a `list`, `tuple[1:3]` returns a `tuple`, and `Vector[1:3]` should return a `Vector`.

### Branch 2: Integer Index

For non-slice keys, we call `operator.index(key)`. This function invokes the `__index__` special method on `key`, which was introduced by PEP 357 to allow NumPy integer types (like `numpy.int32`) to be used as indices. The critical difference from `int()`:

```python
>>> int(3.14)          # 3 -- silently truncates
>>> operator.index(3.14)
# TypeError: 'float' object cannot be interpreted as an integer
```

A float should never be an index. Using `operator.index` enforces this and produces a clear error message. It also eliminates the need for an explicit `isinstance(key, int)` check -- if the key cannot be interpreted as an integer, the function raises `TypeError` automatically.

## Why This Matters

Without slice-aware `__getitem__`, slicing a `Vector` returns a raw `array`:

```python
# Naive delegation
>>> v7 = Vector(range(7))
>>> v7[1:4]
array('d', [1.0, 2.0, 3.0])   # lost all Vector behavior!
```

With the corrected version:

```python
>>> v7[1:4]
Vector([1.0, 2.0, 3.0])       # still a Vector!
>>> abs(v7[1:4])               # magnitude works
5.385...
```

The sliced result retains all `Vector` methods -- `abs()`, `__format__`, hashing -- because it is a proper `Vector` instance.

## The `isinstance` Exception

Using `isinstance` is generally discouraged in duck-typed Python code. However, checking `isinstance(key, slice)` in `__getitem__` is one of the universally accepted exceptions. The built-in `list.__getitem__` does the same thing internally. There is no protocol-based alternative: you need to know whether you received a slice or an integer to decide what to return.

## The `slice.indices` Method

The `slice` object's `indices(length)` method is a hidden gem. It normalizes a slice for a given sequence length, handling:

- Missing values (`None` for start, stop, or step)
- Negative indices
- Indices that exceed the sequence length

```python
>>> slice(None, 10, 2).indices(5)  # [:10:2] on len-5 seq
(0, 5, 2)
>>> slice(-3, None, None).indices(5)  # [-3:] on len-5 seq
(2, 5, 1)
```

You do not need `indices()` when delegating to a container that already handles slices (like `array`). But if you are implementing a sequence backed by something other than a Python sequence -- a database cursor, a memory-mapped file, a network stream -- `slice.indices` saves you from reimplementing all that normalization logic.

## Multidimensional Indexing

When you write `s[1:4, 9]`, Python passes a *tuple* `(slice(1, 4, None), 9)` to `__getitem__`. Our `Vector` does not support this, and `operator.index` on a tuple raises `TypeError` with a helpful message:

```python
>>> v7[1, 2]
TypeError: 'tuple' object cannot be interpreted as an integer
```

NumPy arrays do support multidimensional indexing through this mechanism. For our purposes, the error message is clear enough.

## Gotchas

- **Forgetting to return the same type**: The most common mistake is returning a raw list or array from a sliced `__getitem__`. Always wrap the result in your class constructor.
- **Using `int()` instead of `operator.index()`**: `int(3.14)` silently truncates to 3, which could cause hard-to-find bugs if someone accidentally passes a float index.
- **Subclasses break with hardcoded class names**: Use `type(self)` or `cls = type(self)` instead of `Vector(...)` directly, so that subclasses of `Vector` get instances of the subclass back when slicing.
- **`slice.indices` is not always needed**: If you delegate to a Python sequence that already handles slices, calling `indices` is unnecessary overhead.

## See Also

- [[vector-multidimensional-sequence]] -- The baseline Vector that this version extends
- [[protocols-and-duck-typing]] -- Why `isinstance(key, slice)` is acceptable here
- [[slicing]] -- Chapter 2's coverage of slice syntax and objects
- [[dynamic-attribute-access]] -- The next step in Vector's evolution
