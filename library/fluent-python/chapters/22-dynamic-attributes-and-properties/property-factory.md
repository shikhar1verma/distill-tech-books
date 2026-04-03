---
title: "Coding a Property Factory"
book: "Fluent Python"
chapter: 22
tags: [python, property, factory, closures, metaprogramming, DRY]
related:
  - "[[property-for-validation]]"
  - "[[computed-properties]]"
  - "[[validated-descriptor-pattern]]"
---

# Coding a Property Factory

> **When the same validation logic applies to multiple attributes, a property factory function eliminates repetition by returning a `property()` object whose getter and setter closures capture the storage name.**

## The Problem: Repetitive Properties

In `LineItem`, both `weight` and `price` need identical validation ("must be greater than zero"). Writing separate `@property` getter/setter pairs for each means duplicating roughly 10 lines of code per attribute. As Paul Graham warned: "When I see patterns in my programs, I consider it a sign of trouble."

## The Solution: A `quantity()` Factory

A factory function that builds and returns a `property` object:

```python
def quantity(storage_name):
    """Property factory: rejects zero or negative values."""

    def qty_getter(instance):
        return instance.__dict__[storage_name]

    def qty_setter(instance, value):
        if value > 0:
            instance.__dict__[storage_name] = value
        else:
            raise ValueError('value must be > 0')

    return property(qty_getter, qty_setter)
```

Usage is clean and DRY:

```python
class LineItem:
    weight = quantity('weight')
    price  = quantity('price')

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight    # triggers property setter
        self.price = price      # triggers property setter

    def subtotal(self):
        return self.weight * self.price
```

## How It Works: Closures and `__dict__`

Each call to `quantity()` creates a fresh pair of inner functions (`qty_getter` and `qty_setter`) that close over the `storage_name` parameter. When `quantity('weight')` is called:

1. `storage_name` is bound to `'weight'` in the enclosing scope.
2. `qty_getter` and `qty_setter` are defined, capturing `storage_name` in their closures.
3. A `property` object is constructed from those two functions and returned.
4. The returned property is assigned to the `weight` class attribute.

### Why `instance.__dict__` Instead of `instance.weight`?

Inside `qty_getter` and `qty_setter`, we access `instance.__dict__[storage_name]` directly instead of using `getattr(instance, storage_name)` or `instance.weight`. This is critical because:

- **Reading** `instance.weight` would trigger the property getter, causing infinite recursion.
- **Writing** `instance.weight = value` would trigger the property setter, also causing infinite recursion.
- **`instance.__dict__`** bypasses the descriptor protocol entirely, going straight to the instance's attribute storage.

This pattern -- using `__dict__` to bypass property/descriptor logic -- is a fundamental Python metaprogramming technique.

### Why `instance` Instead of `self`?

The first argument of `qty_getter` and `qty_setter` is named `instance` rather than `self`. This is a naming convention: these functions are not methods defined in a class body. They are standalone functions that happen to receive an instance as their first argument when the `property` machinery calls them. Using `self` would be misleading.

## The Name Duplication Issue

There is one inelegance:

```python
weight = quantity('weight')
```

You must type `weight` twice -- once as the class attribute name (left side) and once as the storage name argument (right side). The property has no way to know what class attribute name it will be assigned to, because the right-hand side is evaluated before the assignment.

This limitation is the motivation for **descriptors with `__set_name__`** (Python 3.6+), covered in Chapter 23. With a descriptor class, `__set_name__` is called automatically during class creation, receiving the attribute name:

```python
class Quantity:
    def __set_name__(self, owner, name):
        self.storage_name = name  # no duplication!
```

## Exploring the Storage

The factory approach uses the **same name** for both the property and the instance storage:

```python
>>> nutmeg = LineItem('Moluccan nutmeg', 8, 13.95)
>>> nutmeg.__dict__
{'description': 'Moluccan nutmeg', 'weight': 8, 'price': 13.95}
```

This works because properties are overriding descriptors. When you access `nutmeg.weight`, Python finds the `weight` property on `LineItem` (the class) before it ever looks in `nutmeg.__dict__`. The property's getter then reads from `nutmeg.__dict__['weight']` directly.

## When to Graduate to Descriptors

The property factory is elegant for simple validation, but descriptors (Chapter 23) are more powerful when you need:

- **Inheritance and subclassing** of validation logic.
- **Automatic name detection** via `__set_name__`.
- **Different validation strategies** (e.g., type checking, range checking, regex matching) that share a common base.
- **Reuse across multiple classes** without importing a factory function.

The `quantity` factory is the stepping stone -- it teaches the closure-based mechanics that underpin how descriptors work at a higher level of abstraction.

## Connections

- This pattern builds on the validation property from [[property-for-validation]].
- The descriptor-based evolution of this pattern is in [[validated-descriptor-pattern]].
- Closures, which make the factory work, are covered in Chapter 9 (Decorators and Closures).
- The rule that properties override instance attributes is explained in [[computed-properties]].
