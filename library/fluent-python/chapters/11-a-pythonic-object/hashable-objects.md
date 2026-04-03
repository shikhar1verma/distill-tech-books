---
slug: hashable-objects
title: "Hashable Objects: __hash__ and __eq__"
chapter: 11
book: fluent-python
type: code-heavy
depends_on:
  - object-representations
tags: [python, hashable, dunder-methods, sets, dict-keys, immutability]
---

# Hashable Objects: `__hash__` and `__eq__`

## Summary

To use custom objects as `dict` keys or `set` members, they must be hashable. This requires implementing both `__hash__` (returning an `int`) and `__eq__`. The critical invariant is: objects that compare equal must have the same hash value. Because hash values should never change over the lifetime of an object, hashable objects should be made effectively immutable -- typically by using private attributes with read-only properties.

## How It Works

### The hashability contract

Python's hash-based collections (`dict`, `set`, `frozenset`) depend on two guarantees:

1. `a == b` implies `hash(a) == hash(b)` (equal objects, equal hashes)
2. The hash of an object never changes during its lifetime

If either guarantee is violated, objects silently "disappear" from dicts and sets.

### Default behavior

By default, user-defined classes inherit `__hash__` from `object`, which returns a value based on `id()` (the memory address). Two distinct instances are never equal (unless you override `__eq__`). The moment you define `__eq__` without `__hash__`, Python sets `__hash__` to `None`, making instances unhashable:

```python
class Vector2d:
    def __eq__(self, other):
        return tuple(self) == tuple(other)

hash(Vector2d(3, 4))  # TypeError: unhashable type: 'Vector2d'
```

### Making Vector2d hashable

The recipe involves three steps:

**Step 1: Make attributes private and read-only**

```python
class Vector2d:
    def __init__(self, x, y):
        self.__x = float(x)  # private (name-mangled)
        self.__y = float(y)

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y
```

**Step 2: Implement `__eq__`**

```python
    def __eq__(self, other):
        return tuple(self) == tuple(other)
```

**Step 3: Implement `__hash__`**

```python
    def __hash__(self):
        return hash((self.x, self.y))
```

The `hash()` of a tuple mixes the hashes of its elements, which satisfies the contract: if two vectors have the same `x` and `y`, their tuples are equal, and `hash()` on equal tuples returns the same value.

### XOR alternative

The Python docs suggest using XOR to combine component hashes:

```python
def __hash__(self):
    return hash(self.x) ^ hash(self.y)
```

Using `hash((self.x, self.y))` is simpler and delegates to the well-tested tuple hashing. Both approaches are valid, but the tuple approach is recommended by Ramalho for its simplicity.

## In Practice

### When to make objects hashable

- **Data classes used as dict keys or set members**: Geographic coordinates, color values, configuration identifiers.
- **Value objects**: Instances that represent values rather than entities. Two `Money(10, 'USD')` instances should be interchangeable.
- **Collections of unique items**: If you want to deduplicate objects using a `set`, they must be hashable.

### The immutability connection

Technically, Python does not require hashable objects to be immutable. You can implement `__hash__` on a mutable object. But if the object mutates in a way that changes what `__eq__` returns, it will violate the hashability contract. An object placed in a set with `hash(obj) == 42` that later mutates to `hash(obj) == 99` becomes invisible to the set -- it is stored at position 42 but lookups compute position 99.

The safe approach: make all attributes that participate in `__eq__` and `__hash__` effectively immutable using private storage and read-only properties.

### Using `__hash__` with `__slots__`

`__slots__` and `__hash__` combine well: `__slots__` prevents adding new attributes, reinforcing immutability. However, `__slots__` alone does not prevent overwriting existing slots. You still need `@property` for true read-only access.

### Pattern matching support

Python 3.10+ uses `__match_args__` for positional pattern matching. This is separate from `__hash__`/`__eq__`, but the full `Vector2d` implementation combines all three:

```python
class Vector2d:
    __match_args__ = ('x', 'y')
    typecode = 'd'

    def __init__(self, x, y):
        self.__x = float(x)
        self.__y = float(y)
    # ... properties, __hash__, __eq__ ...
```

## Common Pitfalls

1. **Implementing `__eq__` without `__hash__`**: Python explicitly sets `__hash__ = None` if you define `__eq__` without `__hash__`, making instances unhashable. This is a safety measure, not a bug.

2. **Mutable components in the hash**: If `self.x` can change after the object is placed in a set, the object becomes unreachable. Always ensure components used in `__hash__` cannot be modified.

3. **Hash/equality mismatch**: If `__eq__` uses attributes that `__hash__` does not consider, two objects can be equal but have different hashes, violating the contract. Always use the same attributes for both.

4. **Overly broad `__eq__`**: The `Vector2d.__eq__` in the chapter compares `tuple(self) == tuple(other)`, which makes `Vector2d(3, 4) == [3, 4]` return `True`. For stricter typing, check `isinstance(other, Vector2d)` first, or return `NotImplemented` for unknown types.

5. **Forgetting that `hash()` must return an `int`**: The return value of `__hash__` must be an integer. Returning a float or string will raise a `TypeError`.

## See Also

- [[read-only-properties]] -- The mechanism used to enforce immutability for hashable objects
- [[private-and-protected-attributes]] -- Name mangling that backs the read-only properties
- [[slots]] -- Memory-efficient storage that also discourages attribute mutation
- Chapter 3 of Fluent Python -- "What Is Hashable" (p. 84)
- Python docs: [object.__hash__](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
