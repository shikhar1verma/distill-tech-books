---
title: "Shallow vs Deep Copies"
slug: shallow-vs-deep-copies
chapter: 6
book: fluent-python
type: code-heavy
depends_on:
  - variables-are-labels
  - relative-immutability-of-tuples
tags: [copy, deepcopy, shallow-copy, deep-copy, aliasing, clone]
---

# Shallow vs Deep Copies

## The Problem

When you "copy" a collection, how deep should the duplication go? Python gives you two choices:

| Method | What is duplicated | Inner objects |
|--------|-------------------|---------------|
| **Shallow** | The outermost container | Shared (references copied) |
| **Deep** | Everything, recursively | Independent clones |

## Making Shallow Copies

Several ways to create a shallow copy:

```python
original = [3, [66, 55], (7, 8, 9)]

# Any of these produce a shallow copy:
a = list(original)        # constructor
b = original[:]           # slice
c = original.copy()       # .copy() method

import copy
d = copy.copy(original)   # copy.copy()
```

All four produce a new list containing the **same references** as the original.

## Why Shallow Copies Can Bite

```python
l1 = [3, [66, 55, 44], (7, 8, 9)]
l2 = list(l1)              # shallow copy

l1.append(100)             # only affects l1 (top-level change)
l1[1].remove(55)           # affects BOTH -- they share the inner list

print(l1)  # [3, [66, 44], (7, 8, 9), 100]
print(l2)  # [3, [66, 44], (7, 8, 9)]
```

The inner list at index `[1]` is the same object in both `l1` and `l2`. Removing `55` from one is visible in the other.

### The `+=` twist

```python
l2[1] += [33, 22]   # list += extends in-place -> shared mutation
l2[2] += (10, 11)   # tuple += creates NEW tuple -> not shared

l1[1] is l2[1]  # True  -- still the same list
l1[2] is l2[2]  # False -- different tuples now
```

## Making Deep Copies

Use `copy.deepcopy()` when you need full independence:

```python
import copy

class Bus:
    def __init__(self, passengers=None):
        self.passengers = list(passengers) if passengers else []

    def drop(self, name):
        self.passengers.remove(name)

bus1 = Bus(["Alice", "Bill", "Claire"])
bus2 = copy.copy(bus1)       # shallow
bus3 = copy.deepcopy(bus1)   # deep

bus1.drop("Bill")

bus2.passengers  # ["Alice", "Claire"] -- Bill gone (shared list)
bus3.passengers  # ["Alice", "Bill", "Claire"] -- independent copy
```

## Cyclic References

`deepcopy` handles cycles gracefully by remembering objects it has already copied:

```python
a = [10, 20]
b = [a, 30]
a.append(b)    # a -> b -> a (cycle)

c = copy.deepcopy(a)  # works fine, no infinite loop
```

## Customizing Copy Behavior

You can control how your objects are copied by implementing:

- `__copy__()` -- called by `copy.copy()`
- `__deepcopy__()` -- called by `copy.deepcopy()`

This is useful when some attributes reference external resources or singletons that should not be duplicated.

## When to Use Which

| Situation | Recommendation |
|-----------|---------------|
| All items are immutable | Shallow copy is fine |
| Contains mutable items you will not modify | Shallow copy is fine |
| Contains mutable items and you need independence | **Deep copy** |
| Performance-critical with large nested structures | Consider shallow + selective copying |

## Key Takeaway

> Copies are shallow by default in Python. A shallow copy duplicates the container but shares all inner references. Use `copy.deepcopy()` when you need a fully independent clone, especially when nested mutable objects are involved.
