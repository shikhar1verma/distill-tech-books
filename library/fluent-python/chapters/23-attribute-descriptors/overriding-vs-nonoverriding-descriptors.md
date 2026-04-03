---
title: "Overriding vs Nonoverriding Descriptors"
book: "Fluent Python"
chapter: 23
tags: [python, descriptors, data-model, attribute-lookup]
related:
  - "[[descriptor-protocol]]"
  - "[[methods-are-descriptors]]"
  - "[[descriptor-usage-tips]]"
---

# Overriding vs Nonoverriding Descriptors

> **Descriptors with `__set__` (overriding) always intercept attribute writes; those without it (nonoverriding) can be shadowed by instance attributes.**

## How It Works

Python divides descriptors into two categories based on whether they implement `__set__`:

**Overriding descriptors** (also called data descriptors or enforced descriptors) implement `__set__`. They intercept both reads and writes. Even if you store a value directly in `instance.__dict__` under the same name, the descriptor's `__get__` still wins on the next read. The `property` built-in produces overriding descriptors.

**Nonoverriding descriptors** (also called non-data descriptors or shadowable descriptors) implement only `__get__`. They handle reads, but any write to the same attribute name on an instance creates a regular instance attribute that shadows the descriptor. Functions are nonoverriding descriptors, which is why you can shadow a method by assigning to an instance attribute.

```python
class Overriding:
    """Has __set__ -- intercepts writes, can't be shadowed."""
    def __get__(self, instance, owner):
        return 'descriptor value'
    def __set__(self, instance, value):
        print(f'Overriding.__set__ intercepted {value!r}')

class NonOverriding:
    """No __set__ -- can be shadowed by instance attribute."""
    def __get__(self, instance, owner):
        return 'descriptor value'

class MyClass:
    over = Overriding()
    non_over = NonOverriding()

obj = MyClass()

# Overriding: descriptor always controls reads
obj.__dict__['over'] = 'instance value'
print(obj.over)        # 'descriptor value' -- descriptor wins

# Nonoverriding: instance attribute shadows descriptor
obj.non_over = 'instance value'
print(obj.non_over)    # 'instance value' -- instance wins
```

The asymmetry comes from Python's attribute lookup algorithm. For reads, Python checks for overriding descriptors (data descriptors) on the class **before** checking `instance.__dict__`. For nonoverriding descriptors, `instance.__dict__` is checked first. For writes, only overriding descriptors intercept; without `__set__`, the write goes directly to `instance.__dict__`.

There is also a hybrid case: an overriding descriptor without `__get__`. It has `__set__` so it intercepts writes, but reads fall back to the normal lookup. If an instance attribute of the same name exists, reads return the instance attribute value. Writes still go through the descriptor.

## In Practice

**Overriding descriptors** are the right choice for:
- Validation (like `Quantity` -- you must intercept every write)
- Read-only attributes (implement `__set__` to raise `AttributeError`)
- Properties (which are overriding descriptors under the hood)

**Nonoverriding descriptors** are the right choice for:
- Caching: compute a value in `__get__`, store it as an instance attribute, and future reads bypass the descriptor entirely. This is exactly how `functools.cached_property` works.
- Methods: functions are nonoverriding descriptors, which is why method lookup works through `__get__`.

The shadowing behavior of nonoverriding descriptors is also why you can monkey-patch a single instance by assigning to its attributes without affecting the class or other instances.

A subtle but important rule: descriptors can always be overwritten by assigning to the **class** itself. `MyClass.over = 99` replaces the descriptor entirely, regardless of whether it's overriding or not. To control writes on the class, you'd need to attach a descriptor to the metaclass.

## Common Pitfalls

- **Forgetting `__set__` on a read-only descriptor**: If you implement only `__get__` for a "read-only" attribute, users can shadow it by assigning an instance attribute. Always implement `__set__` that raises `AttributeError` for true read-only behavior.
- **Assuming nonoverriding descriptors are broken**: Shadowing is a feature, not a bug. It enables caching patterns and is consistent with how methods work.
- **Overwriting descriptors on the class by accident**: Assigning to the class attribute replaces the descriptor. This is a form of monkey-patching that can break dependent instances.

## See Also

- [[descriptor-protocol]] -- the underlying `__get__`/`__set__`/`__delete__` methods
- [[methods-are-descriptors]] -- functions as nonoverriding descriptors
- [[descriptor-usage-tips]] -- choosing the right descriptor strategy
