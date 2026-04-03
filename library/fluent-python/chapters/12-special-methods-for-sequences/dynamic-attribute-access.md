---
title: "Dynamic Attribute Access: __getattr__ and __setattr__"
book: "Fluent Python"
chapter: 12
tags: [python, __getattr__, __setattr__, dynamic-attributes, __match_args__, attribute-lookup]
type: "code-heavy"
depends_on:
  - "[[vector-multidimensional-sequence]]"
related:
  - "[[sliceable-sequence-getitem]]"
  - "[[hashing-and-eq]]"
  - "[[formatting-with-format]]"
  - "[[descriptor-protocol]]"
---

## Summary

`__getattr__` provides fallback attribute lookup: Python calls it only when the normal lookup chain (instance `__dict__`, class, superclasses) fails to find the attribute. This makes it perfect for providing shorthand access like `v.x` for `v[0]` on a `Vector` with potentially thousands of components. However, implementing `__getattr__` without a corresponding `__setattr__` creates a subtle inconsistency: `v.x = 10` silently creates an instance attribute that shadows the dynamic lookup, making `v.x` return 10 while the underlying component remains unchanged. The fix is to implement `__setattr__` to block writes to the shorthand names.

## How `__getattr__` Works

Python's attribute lookup follows a specific order:

1. Check the instance's `__dict__` for the attribute.
2. Check the class and its superclasses (following the MRO).
3. If the attribute is still not found, call `__getattr__(self, name)`.

The key detail is step 3: `__getattr__` is a **fallback**. It is never called if the attribute is found through normal means. This is different from `__getattribute__`, which is called for *every* attribute access (and is much harder to use correctly).

## The Implementation

```python
class Vector:
    __match_args__ = ('x', 'y', 'z', 't')

    def __getattr__(self, name):
        cls = type(self)
        try:
            pos = cls.__match_args__.index(name)
        except ValueError:
            pos = -1
        if 0 <= pos < len(self._components):
            return self._components[pos]
        msg = f'{cls.__name__!r} object has no attribute {name!r}'
        raise AttributeError(msg)
```

The method looks up `name` in `__match_args__` to find its position, then returns the corresponding component. If the name is not in `__match_args__`, or the vector does not have enough components, it raises `AttributeError` -- which is the expected behavior for missing attributes.

### The `__match_args__` Dual Purpose

`__match_args__` was introduced in Python 3.10 for structural pattern matching. Setting it to `('x', 'y', 'z', 't')` means:

```python
match v:
    case Vector(x, y):  # positional patterns work via __match_args__
        print(f'2D: ({x}, {y})')
```

In our `Vector`, `__match_args__` also serves as the registry of valid shorthand attribute names for `__getattr__` and `__setattr__`. One tuple, two uses.

## The Inconsistency Bug

Without `__setattr__`, this happens:

```python
>>> v = Vector(range(5))
>>> v.x               # __getattr__ returns v[0]
0.0
>>> v.x = 10          # creates instance attribute v.__dict__['x'] = 10
>>> v.x               # instance __dict__ found first -- __getattr__ NOT called
10
>>> v[0]              # underlying component is STILL 0.0
0.0
```

The assignment `v.x = 10` creates a new entry in `v.__dict__`. On subsequent access, Python finds `'x'` in the instance dict (step 1 of lookup) and returns 10 without ever calling `__getattr__`. The vector's actual data is unchanged.

This is not a bug in Python -- it is the documented behavior of `__getattr__`. The bug is in our code: we provided a read path (`__getattr__`) without guarding the write path.

## The Fix: `__setattr__`

```python
def __setattr__(self, name, value):
    cls = type(self)
    if len(name) == 1:
        if name in cls.__match_args__:
            error = 'readonly attribute {attr_name!r}'
        elif name.islower():
            error = "can't set attributes 'a' to 'z' in {cls_name!r}"
        else:
            error = ''
        if error:
            msg = error.format(cls_name=cls.__name__, attr_name=name)
            raise AttributeError(msg)
    super().__setattr__(name, value)
```

The logic:

1. **Single-letter, in `__match_args__`**: Raise `AttributeError` saying it is a readonly attribute.
2. **Single-letter, lowercase, not in `__match_args__`**: Also block it, to avoid confusion.
3. **Single-letter, uppercase**: Allow (unlikely conflict).
4. **Multi-letter names**: Delegate to `super().__setattr__` for normal behavior.

The call to `super().__setattr__` in the default case is essential. Without it, no instance attributes could ever be set -- including `_components` in `__init__`.

## Why Not `__slots__`?

It might seem tempting to use `__slots__` to prevent arbitrary instance attributes. However, `__slots__` has its own set of issues (memory layout complications with inheritance, interference with weak references, etc.) and should be used only when memory optimization is the primary goal, not as an access-control mechanism.

## Design Principle

**Whenever you implement `__getattr__`, implement `__setattr__` too.** This is not just advice for `Vector` -- it is a general rule. Any class that provides dynamic attribute reads through `__getattr__` is vulnerable to the shadowing inconsistency unless writes are also controlled. The specific policy (block writes, redirect writes to the underlying data, or allow them freely) depends on your design, but ignoring the write path is always a bug waiting to happen.

## In Practice

Dynamic attribute access is most useful when:

- You have a small, fixed set of meaningful names for positions in a sequence (like `x`, `y`, `z` for spatial coordinates).
- You want to support pattern matching via `__match_args__`.
- The underlying data is stored in a non-dict container (array, struct, database row).

For classes with a large or open-ended set of dynamic attributes, consider `__getattribute__` or descriptors instead.

## Gotchas

- **`__getattr__` is a fallback only**: It is not called when the attribute exists in the instance dict or class. If you need to intercept *every* access, use `__getattribute__` (but be very careful about infinite recursion).
- **Must raise `AttributeError`**: If `__getattr__` does not find the attribute, it *must* raise `AttributeError`. Returning `None` or silently failing will mask bugs.
- **Instance attributes shadow `__getattr__`**: This is by design in Python. The fix is `__setattr__`, not trying to change the lookup order.
- **`super().__setattr__` is mandatory in the default branch**: Forgetting it means `__init__` cannot set `self._components`.

## See Also

- [[vector-multidimensional-sequence]] -- The baseline class this extends
- [[sliceable-sequence-getitem]] -- The `__getitem__` that `__getattr__` wraps
- [[descriptor-protocol]] -- Chapter 23's deeper mechanism for attribute access
- [[hashing-and-eq]] -- The next step: making Vector hashable
