---
title: "The Descriptor Protocol"
book: "Fluent Python"
chapter: 23
tags: [python, descriptors, data-model, oop]
related:
  - "[[overriding-vs-nonoverriding-descriptors]]"
  - "[[validated-descriptor-pattern]]"
  - "[[methods-are-descriptors]]"
  - "[[descriptor-usage-tips]]"
---

# The Descriptor Protocol

> **A descriptor is a class implementing `__get__`, `__set__`, and/or `__delete__` that manages attribute access on behalf of another class.**

## How It Works

A descriptor is any object whose class defines one or more of the special methods `__get__`, `__set__`, or `__delete__`. When an instance of such a class is stored as a **class attribute** of another class (the managed class), Python intercepts attribute access on managed instances and routes it through the descriptor's methods instead of performing normal attribute lookup.

The descriptor protocol methods have these signatures:

```python
def __get__(self, instance, owner):
    # self: the descriptor instance
    # instance: the managed instance (None if accessed via class)
    # owner: the managed class
    ...

def __set__(self, instance, value):
    # self: the descriptor instance
    # instance: the managed instance
    # value: the value being assigned
    ...

def __delete__(self, instance):
    # self: the descriptor instance
    # instance: the managed instance
    ...

def __set_name__(self, owner, name):
    # Called once during class creation (Python 3.6+)
    # owner: the managed class
    # name: the attribute name this descriptor was assigned to
    ...
```

Here is a complete working example -- a `Quantity` descriptor that rejects non-positive values:

```python
class Quantity:
    def __set_name__(self, owner, name):
        self.storage_name = name

    def __set__(self, instance, value):
        if value > 0:
            instance.__dict__[self.storage_name] = value
        else:
            raise ValueError(f'{self.storage_name} must be > 0')


class LineItem:
    weight = Quantity()  # descriptor instances as class attributes
    price = Quantity()

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight   # triggers Quantity.__set__
        self.price = price

    def subtotal(self):
        return self.weight * self.price
```

Key terminology you'll encounter when working with descriptors:
- **Descriptor class**: the class implementing the protocol (e.g., `Quantity`)
- **Managed class**: the class where descriptor instances live as class attributes (e.g., `LineItem`)
- **Managed instance**: an instance of the managed class (e.g., a particular `LineItem`)
- **Storage attribute**: the instance attribute where the actual value is kept
- **Managed attribute**: the public attribute handled by the descriptor

## In Practice

Descriptors are the backbone of several Python features: `property`, `classmethod`, `staticmethod`, `functools.cached_property`, and even plain methods all use the descriptor protocol. ORMs like Django and SQLAlchemy use descriptors to manage database field access.

Use descriptors when you need the same attribute-access logic across multiple attributes or multiple classes. A single `Quantity` descriptor class can validate dozens of numeric fields across your entire codebase. Without descriptors, you'd need to repeat the same `@property` getter/setter pattern for every field.

The `__set_name__` method (Python 3.6+) is essential for ergonomic descriptors. Before it existed, users had to pass the attribute name explicitly: `weight = Quantity('weight')`. With `__set_name__`, the interpreter passes the name automatically during class creation.

## Common Pitfalls

- **Storing values on the descriptor instead of the instance**: The descriptor object is a class attribute, shared among all instances. Writing `self.__dict__[name] = value` (where `self` is the descriptor) means all instances share one value. Always store in `instance.__dict__`.
- **Infinite recursion via `setattr`**: Inside `__set__`, calling `setattr(instance, name, value)` triggers the descriptor's `__set__` again. Always write to `instance.__dict__` directly.
- **Forgetting `__get__` returns for class access**: When `instance` is `None` (accessed via the class), return `self` to support introspection. Without this guard, you'll get `KeyError` or `AttributeError`.

## See Also

- [[overriding-vs-nonoverriding-descriptors]] -- how `__set__` presence changes shadowing behavior
- [[validated-descriptor-pattern]] -- reusable validation with descriptor inheritance
- [[methods-are-descriptors]] -- how functions use `__get__` to create bound methods
- [[descriptor-usage-tips]] -- when to use property vs custom descriptors
