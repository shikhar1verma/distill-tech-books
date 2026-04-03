---
slug: read-only-properties
title: "Read-Only Properties and Immutability"
chapter: 11
book: fluent-python
type: code-heavy
depends_on:
  - private-and-protected-attributes
  - hashable-objects
tags: [python, property, immutability, descriptors, encapsulation]
---

# Read-Only Properties and Immutability

## Summary

Using `@property` with only a getter (no setter) combined with private backing attributes (`__x`) creates effectively read-only access to instance data. This is the Pythonic alternative to Java-style getter methods, and it is a prerequisite for safe hashability -- since an object's hash must never change, the attributes that feed `__hash__` and `__eq__` must be protected from modification.

## How It Works

### The `@property` decorator

`@property` turns a method into a descriptor that intercepts attribute access. When you define only the getter, any attempt to set the attribute raises `AttributeError`:

```python
class Vector2d:
    def __init__(self, x, y):
        self.__x = float(x)  # private storage
        self.__y = float(y)

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y
```

Usage:

```python
v = Vector2d(3, 4)
v.x           # 3.0 -- calls the getter
v.x = 7      # AttributeError: can't set attribute 'x'
```

### Why private backing + property?

The pattern has two parts that work together:

1. **`self.__x`** -- a name-mangled attribute stored as `_Vector2d__x`. Direct access to `self.__x` from outside the class requires knowing the mangled name.

2. **`@property def x(self)`** -- provides a clean public interface (`v.x`) that reads the private attribute. Because there is no `@x.setter`, assignment is blocked.

This combination provides "immutability" in scare quotes -- a determined programmer can still write `v._Vector2d__x = 99`. But it prevents accidental mutation, which is the goal.

### The property descriptor under the hood

A `@property` creates a descriptor object at the class level. When Python resolves `v.x`, the lookup finds the property descriptor on the class (which is a data descriptor because it defines `__get__`), and the descriptor's `__get__` calls the getter function. Because data descriptors take priority over instance `__dict__`, even if someone manages to put `'x'` into the instance dict, the property still wins.

### Read-write properties (for contrast)

Chapter 22 covers the full `@property` with both getter and setter:

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError('radius must be >= 0')
        self._radius = value
```

In Chapter 11, we only use the read-only form (getter only) because the goal is immutability.

## In Practice

### The hashability connection

The primary motivation for read-only properties in Chapter 11 is enabling `__hash__`. The reasoning chain:

1. We want `Vector2d` instances usable as dict keys and set members.
2. This requires `__hash__` and `__eq__`.
3. Objects that compare equal must have the same hash.
4. If `x` or `y` could change after the object is in a set, the hash would be stale.
5. Therefore, `x` and `y` must be read-only.

Without read-only properties, nothing prevents:

```python
v = Vector2d(3, 4)
s = {v}          # hash computed from (3, 4)
v.x = 99         # hash is now stale!
v in s           # False -- the set can't find v anymore
```

### Pythonic vs Java-style getters

In Java, every field is typically private with explicit `getX()` / `setX()` methods. Python rejects this pattern. The idiomatic approach:

1. **Start with public attributes** (`self.x = ...`). No property needed.
2. **Add `@property` later if needed** -- to add validation, computed values, or read-only access.

The beauty is that the public API never changes: `obj.x` works whether `x` is a plain attribute or a property. Callers never need to change from `obj.x` to `obj.get_x()`.

### Combining with `__slots__`

When using `__slots__`, the slots themselves create implicit descriptors. You can still layer properties on top, but the backing storage must be in the slots:

```python
class Vector2d:
    __slots__ = ('__x', '__y')

    def __init__(self, x, y):
        object.__setattr__(self, '_Vector2d__x', float(x))
        object.__setattr__(self, '_Vector2d__y', float(y))

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y
```

Note: with `__slots__` and properties, you may need `object.__setattr__()` in `__init__` to bypass the property's lack of a setter. Alternatively, since `__init__` runs inside the class body context, `self.__x = float(x)` works because name mangling applies to the slot.

### Immutability spectrum in Python

Python offers several levels of "immutability" for objects:

| Approach | Protection level |
|---|---|
| Convention (`_x`) | Documentation only |
| Name mangling (`__x`) | Prevents accidental subclass collisions |
| Read-only `@property` + `__x` | Prevents `obj.x = val` |
| `__slots__` without `__dict__` | Prevents adding new attributes |
| `__setattr__` override | Can block ALL attribute setting |
| `frozen=True` dataclass | Blocks setting via `__setattr__` and `__delattr__` |
| `namedtuple` / `frozenset` | Truly immutable (implemented in C) |

The `Vector2d` approach (property + mangling) is a good middle ground: robust enough for hashability, transparent enough for debugging.

## Common Pitfalls

1. **Defining a setter accidentally**: If you add `@x.setter`, the property is no longer read-only. Be deliberate about whether to include a setter.

2. **Trying to set in `__init__`**: If you define `@property def x` with no setter, then `self.x = float(x)` in `__init__` raises `AttributeError`. You must write to the private backing attribute `self.__x` directly.

3. **Assuming properties prevent all mutation**: Properties block `obj.x = val` but not mutation of mutable values. If `self.__data` is a list, `obj.data.append(42)` still mutates it. Return copies or use immutable types for true protection.

4. **Performance overhead**: Each property access involves a function call (the getter). For hot loops accessing millions of times, this overhead can be noticeable compared to direct attribute access. Profile before worrying.

5. **Confusing `@property` with `@cached_property`**: `@cached_property` (from `functools`) computes the value once and stores it as an instance attribute. It requires `__dict__` (incompatible with bare `__slots__`). `@property` recomputes on every access.

## See Also

- [[hashable-objects]] -- The motivation for making `Vector2d` immutable
- [[private-and-protected-attributes]] -- The name mangling behind `__x`
- [[slots]] -- Combining `__slots__` with properties for maximum efficiency
- Chapter 22 of Fluent Python -- Full coverage of `@property` including read-write properties and computed attributes
- Python docs: [property](https://docs.python.org/3/library/functions.html#property)
