---
title: "del, Garbage Collection, and Interning Tricks"
slug: del-garbage-collection-interning
chapter: 6
book: fluent-python
type: theory-heavy
depends_on:
  - identity-equality-aliases
tags: [del, garbage-collection, reference-counting, interning, CPython, weakref, __del__]
---

# del, Garbage Collection, and Interning Tricks

## What `del` Actually Does

`del` is a **statement** (not a function). It removes a **reference** (name), not an object.

```python
a = [1, 2]
b = a
del a          # removes the name 'a', but the list lives on
b              # [1, 2] -- still accessible
```

An object is only destroyed when it becomes **unreachable** -- when no references point to it.

## Reference Counting in CPython

CPython's primary garbage collection mechanism is **reference counting**. Every object carries a count of how many references point to it. When the count drops to zero, the object is immediately destroyed.

```python
import weakref

s1 = {1, 2, 3}
s2 = s1

def bye():
    print("Object destroyed")

ender = weakref.finalize(s1, bye)

del s1            # refcount: 2 -> 1, object survives
s2 = "spam"       # refcount: 1 -> 0, object destroyed -> "Object destroyed"
```

`weakref.finalize` holds a **weak reference** that does not increase the refcount, so the callback fires when all strong references are gone.

## Cyclic Garbage Collector

Reference counting alone cannot handle **reference cycles**:

```python
a = []
b = [a]
a.append(b)   # a -> b -> a (cycle)
del a, b      # refcount never reaches 0!
```

CPython has a **generational garbage collector** (since Python 2.0) that detects and collects groups of objects in reference cycles. It runs periodically and can be controlled via the `gc` module.

## The `__del__` Method

`__del__` is called when an object is about to be destroyed, giving it a chance to release external resources. However:

- It is **not** a destructor you call directly.
- You should rarely implement it in your own classes.
- It may not be called promptly (or at all) in non-CPython implementations.
- Use context managers (`with` statement) for resource cleanup instead.

## Tricks Python Plays with Immutables

### Tuple and String "Copy" Optimization

For immutable types, Python may return the **same object** instead of making a copy:

```python
t1 = (1, 2, 3)
t2 = tuple(t1)
t2 is t1            # True -- same object!

t3 = t1[:]
t3 is t1            # True -- same object!

fs = frozenset([1, 2])
fs.copy() is fs     # True -- "copy" returns itself
```

This is safe because these objects can never change.

### String Interning

CPython **interns** certain strings (and all strings that look like identifiers), reusing a single object for identical string literals:

```python
s1 = "hello"
s2 = "hello"
s1 is s2           # True (interned)
```

### Small Integer Caching

CPython pre-allocates integer objects for the range **-5 to 256**:

```python
a = 256
b = 256
a is b            # True (cached)

a = 257
b = 257
a is b            # May be True or False (implementation-dependent)
```

### The Golden Rule

> **Never depend on interning.** Always use `==` to compare values. The `is` operator should only be used for `None` and sentinel objects.

The interning and caching behavior is an undocumented CPython optimization that varies across Python implementations (PyPy, Jython, etc.) and even across CPython versions.

## Summary Table

| Topic | Key Point |
|-------|-----------|
| `del x` | Removes the name `x`, not the object |
| Reference counting | Object destroyed at refcount == 0 (CPython) |
| Cyclic GC | Handles reference cycles that refcounting misses |
| `__del__` | Rarely needed; prefer context managers |
| Interning | Small ints, some strings shared; never rely on it |
| Immutable "copies" | `tuple(t)`, `t[:]`, `frozenset.copy()` may return same object |

## Key Takeaway

> `del` removes references, not objects. CPython uses reference counting for immediate cleanup and a cyclic GC for cycles. Python optimizes memory by sharing immutable objects (interning), but this is an implementation detail -- always use `==` for value comparisons.
