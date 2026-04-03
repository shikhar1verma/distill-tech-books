---
title: "Slicing"
book: "Fluent Python"
chapter: 2
tags: [slicing, slice-objects, sequences, indexing, mutable-sequences]
related:
  - "[[list-comprehensions-genexps]]"
  - "[[augmented-assignment-sequences]]"
  - "[[augmented-assignment-sequences]]"
---

## Summary

Python's slice notation `s[a:b:c]` supports optional start, stop, and stride. Slicing goes beyond basic extraction: named slice objects improve readability, negative strides reverse sequences, and assigning to slices enables powerful in-place editing of mutable sequences.

## How It Works

### Basic Slicing

The convention of excluding the last item makes arithmetic easy:

```python
l = [10, 20, 30, 40, 50, 60]

l[:3]   # [10, 20, 30]  -- length = 3
l[3:]   # [40, 50, 60]  -- no overlap with l[:3]
l[:3] + l[3:] == l  # True -- always
```

### Stride (Step)

The third parameter `c` in `s[a:b:c]` specifies the step:

```python
s = 'bicycle'
s[::3]    # 'bye'     -- every 3rd character
s[::-1]   # 'elcycib' -- reversed
s[::-2]   # 'eccb'    -- reversed, every 2nd
```

### Slice Objects

The notation `a:b:c` inside `[]` produces a `slice(a, b, c)` object. You can name slices for readability, especially when parsing fixed-width data:

```python
SKU         = slice(0, 6)
DESCRIPTION = slice(6, 40)
UNIT_PRICE  = slice(40, 52)

for line in data:
    print(line[UNIT_PRICE], line[DESCRIPTION])
```

Under the hood, `seq[start:stop:step]` calls `seq.__getitem__(slice(start, stop, step))`.

### Assigning to Slices

On mutable sequences, slice notation on the left side of `=` or as the target of `del` enables in-place editing:

```python
l = list(range(10))

l[2:5] = [20, 30]       # replace 3 items with 2
# [0, 1, 20, 30, 5, 6, 7, 8, 9]

del l[5:7]               # remove items
# [0, 1, 20, 30, 5, 8, 9]

l[3::2] = [11, 22]       # replace at stride
# [0, 1, 20, 11, 5, 22, 9]

l[2:5] = [100]           # replace 3 items with 1
# [0, 1, 100, 22, 9]
```

The right-hand side must be an iterable (even for a single item: use `[100]`, not `100`).

### Multidimensional Slicing

The `[]` operator can take a tuple of indices or slices (e.g., `a[i, j]` or `a[m:n, k:l]`). This is used by NumPy but not by built-in sequences. The `Ellipsis` object (`...`) serves as a shorthand in NumPy for multiple `:` slices.

## In Practice

- **Named slices** are invaluable for parsing flat-file formats, log files, and fixed-width records.
- **Slice assignment** can insert, delete, or replace subsequences in a single expression.
- **Reversed slicing** (`s[::-1]`) is a common Python idiom for reversing any sequence.
- Slicing always returns a **new object** of the same type (a new list from a list, a new string from a string).

## Common Pitfalls

1. **Off-by-one errors.** Remember that `s[a:b]` excludes index `b`. Think of slice indices as pointing *between* elements.
2. **Stride with start/stop.** `s[a:b:c]` can be confusing. When using a negative stride, `a` should be greater than `b`, or omit them: `s[::-1]`.
3. **Slice assignment requires an iterable.** `l[2:5] = 100` raises `TypeError`. Use `l[2:5] = [100]`.
4. **Stride-based assignment must have matching length.** `l[::2] = [1, 2]` fails if the slice selects a different number of elements than the replacement iterable.

## See Also

- [[augmented-assignment-sequences]] -- related in-place modification of sequences
- [[augmented-assignment-sequences]] -- memoryview supports multidimensional slicing
- Chapter 12 covers implementing `__getitem__` with slice support in custom classes
