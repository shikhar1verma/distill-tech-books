---
slug: slots
title: "Saving Memory with __slots__"
chapter: 11
book: fluent-python
type: mixed
depends_on:
  - private-and-protected-attributes
tags: [python, slots, memory-optimization, data-model, performance]
---

# Saving Memory with `__slots__`

## Summary

By default, Python stores instance attributes in a per-instance `__dict__` dictionary, which has significant memory overhead. Defining `__slots__` as a class attribute replaces the per-instance `__dict__` with a fixed-size array of references, dramatically reducing memory consumption -- Ramalho demonstrates a reduction from 1.55 GiB to 551 MiB for 10 million `Vector2d` instances. The tradeoff is loss of dynamic attribute assignment and several inheritance caveats that must be understood before adopting `__slots__`.

## How It Works

### Basic mechanism

When a class defines `__slots__`, Python creates descriptor objects at the class level for each named attribute, and instances use a compact internal array instead of a `__dict__`:

```python
class Pixel:
    __slots__ = ('x', 'y')

p = Pixel()
p.x = 10
p.y = 20
p.color = 'red'  # AttributeError: 'Pixel' object has no attribute 'color'
p.__dict__        # AttributeError: 'Pixel' object has no attribute '__dict__'
```

Two immediate effects: (1) no `__dict__` on instances, and (2) only attributes named in `__slots__` can be set.

### Memory savings

Each Python `dict` carries overhead for the hash table structure (typically 64+ bytes even when nearly empty). For a class with just two float attributes, `__dict__` can easily use 100+ bytes of overhead per instance. With `__slots__`, the overhead drops to roughly the size of the references themselves.

Ramalho's benchmark (10 million `Vector2d` instances):
- With `__dict__`: 1,666 MB (166 bytes/instance)
- With `__slots__`: 578 MB (58 bytes/instance)

That is roughly a 3x reduction. The slotted version also ran faster (8.4s vs 12.0s) due to better cache locality and less garbage collector work.

### How to declare

`__slots__` must be a sequence (tuple, list, or iterable) of strings. Use a tuple by convention to signal immutability:

```python
class Vector2d:
    __match_args__ = ('x', 'y')   # for pattern matching (public names)
    __slots__ = ('__x', '__y')     # for storage (private names)
    typecode = 'd'
```

Note that `__slots__` lists the internal attribute names (which may be mangled private names), while `__match_args__` lists public names.

## In Practice

### When to use `__slots__`

- **Millions of instances**: The primary use case. If your program creates very large numbers of small objects (game entities, database rows, sensor readings), `__slots__` provides meaningful savings.
- **Data-heavy pipelines**: When holding large datasets in memory as Python objects rather than NumPy arrays or pandas DataFrames.
- **Tight inner loops**: The slight speed improvement from slot access (descriptor lookup vs dict lookup) can matter in hot paths.

### When NOT to use `__slots__`

- **Application-level classes with few instances**: The complexity is not worth the negligible savings.
- **Classes that need dynamic attributes**: Any use of `setattr()` with arbitrary names, monkey-patching, or `@cached_property` requires `__dict__`.
- **Mixin classes or ABCs**: These are meant to be subclassed broadly, and requiring every subclass to redeclare `__slots__` is burdensome.

### Inheritance rules

This is where `__slots__` gets tricky.

**Subclass without `__slots__`** -- gets a `__dict__` back:
```python
class OpenPixel(Pixel):
    pass  # no __slots__

op = OpenPixel()
hasattr(op, '__dict__')  # True -- surprise!
op.color = 'green'       # works -- stored in __dict__
op.x = 8                 # works -- stored in slot inherited from Pixel
```

**Subclass with additional `__slots__`** -- extends the parent:
```python
class ColorPixel(Pixel):
    __slots__ = ('color',)  # adds to parent's ('x', 'y')

cp = ColorPixel()
hasattr(cp, '__dict__')  # False
cp.x = 2                 # slot from Pixel
cp.color = 'blue'        # slot from ColorPixel
cp.flavor = 'banana'     # AttributeError
```

**Rule**: To prevent `__dict__` in subclasses, every class in the hierarchy must declare `__slots__` (even if as an empty tuple `()`).

### The `__dict__` escape hatch

You can include `'__dict__'` in `__slots__` to get both slot storage and a dynamic dict:

```python
class Hybrid:
    __slots__ = ('x', 'y', '__dict__')
```

This allows `@cached_property` and dynamic attributes while still gaining slot storage for the named attributes. However, it partially defeats the memory savings.

### Weak references

Instances of classes with `__slots__` cannot be weakly referenced unless you include `'__weakref__'` in the slots:

```python
class Ref:
    __slots__ = ('value', '__weakref__')
```

## Common Pitfalls

1. **Forgetting to redeclare in subclasses**: The single most common mistake. A subclass without `__slots__` silently gets a `__dict__`, negating memory savings for those instances.

2. **Declaring `__slots__` after class creation**: Slots must be present at class definition time. Adding `MyClass.__slots__ = ('x',)` after the fact has no effect on instances.

3. **Duplicate slot names in hierarchy**: If a subclass re-declares a slot name already in the parent's `__slots__`, it wastes memory (the slot is allocated twice). Python 3.x may raise a warning or silently create redundant descriptors.

4. **Assuming `__slots__` makes objects immutable**: Slots restrict which attributes exist but do not prevent overwriting existing slot values. For immutability, combine `__slots__` with read-only `@property`.

5. **Using `__slots__` with multiple inheritance**: If two base classes both define `__slots__` with non-empty tuples, layout conflicts can arise. Only one base class can have a non-empty `__slots__` (the other must use `__slots__ = ()`).

6. **Breaking introspection and serialization**: Some libraries expect `__dict__` for serialization (e.g., `json.dumps(obj.__dict__)`). Slotted objects require custom serialization logic.

## See Also

- [[private-and-protected-attributes]] -- Name mangling interacts with slot names
- [[hashable-objects]] -- Slots reinforce the immutability needed for hashability
- [[overriding-class-attributes]] -- Class attributes like `typecode` coexist with `__slots__` (they live on the class, not the instance)
- Python docs: [__slots__](https://docs.python.org/3/reference/datamodel.html#slots)
- For large-scale numeric data, consider NumPy arrays or pandas instead of millions of slotted Python objects
