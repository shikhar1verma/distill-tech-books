---
title: "Using Properties for Attribute Validation"
book: "Fluent Python"
chapter: 22
tags: [python, property, validation, getter-setter, encapsulation]
related:
  - "[[computed-properties]]"
  - "[[property-factory]]"
  - "[[attribute-deletion]]"
  - "[[descriptor-protocol]]"
---

# Using Properties for Attribute Validation

> **A read/write property lets you add validation to a public attribute without changing the class interface. Callers still write `obj.weight = 5` -- they never know a setter is running behind the scenes.**

## The Problem: Garbage In, Garbage Out

Consider a simple `LineItem` class for an order system:

```python
class LineItem:
    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price

    def subtotal(self):
        return self.weight * self.price
```

Nothing prevents a negative weight:

```python
raisins = LineItem('Golden raisins', 10, 6.95)
raisins.weight = -20     # garbage in...
raisins.subtotal()       # -139.0 -- garbage out!
```

Jeff Bezos famously discovered that early Amazon customers could order negative quantities of books, receiving credit to their credit cards.

## The Solution: Read/Write Properties

Instead of changing the interface (e.g., adding `get_weight()`/`set_weight()`), Python lets you turn the public `weight` attribute into a property. Existing code that does `item.weight = 12` continues to work -- the property setter runs transparently:

```python
class LineItem:
    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight   # triggers the setter
        self.price = price

    def subtotal(self):
        return self.weight * self.price

    @property
    def weight(self):
        return self.__weight

    @weight.setter
    def weight(self, value):
        if value > 0:
            self.__weight = value
        else:
            raise ValueError('value must be > 0')
```

Key details:

- **The getter, setter, and the public name all share the same name: `weight`.** This is required by the decorator syntax.
- **Storage uses a private attribute `self.__weight`** (name-mangled to `_LineItem__weight`). This prevents direct access from bypassing validation.
- **The setter runs during `__init__`** because `self.weight = weight` triggers the property. This means invalid objects can never be created.
- **`ValueError` is the idiomatic exception** for invalid argument values.

## The `property()` Constructor

`property` is actually a class, not a function. Its full constructor signature:

```python
property(fget=None, fset=None, fdel=None, doc=None)
```

All arguments are optional. If `fset` is not provided, attempting to set the attribute raises `AttributeError`. If `fdel` is not provided, `del obj.attr` raises `AttributeError`.

### Decorator Syntax vs. Classic Syntax

The decorator approach:

```python
@property
def weight(self):
    """Weight in kilograms."""
    return self.__weight

@weight.setter
def weight(self, value):
    if value > 0:
        self.__weight = value
    else:
        raise ValueError('value must be > 0')
```

The equivalent classic approach:

```python
def get_weight(self):
    return self.__weight

def set_weight(self, value):
    if value > 0:
        self.__weight = value
    else:
        raise ValueError('value must be > 0')

weight = property(get_weight, set_weight, doc='Weight in kilograms.')
```

The classic syntax is sometimes clearer, especially in property factories (see [[property-factory]]). The decorator syntax is preferred in regular class bodies because it makes the getter/setter relationship visually obvious.

## Property Documentation

- When using the decorator syntax, the **getter's docstring** becomes the property's `__doc__`.
- When using the classic syntax, pass the `doc` argument explicitly.
- Tools like `help()` and IDEs extract documentation from `property.__doc__`.

```python
class Foo:
    @property
    def bar(self):
        """The bar attribute."""
        return self.__dict__['bar']
```

`help(Foo.bar)` will display "The bar attribute."

## Why Not Java-Style Getters and Setters?

In Java, best practice requires private fields with explicit `getField()`/`setField()` methods, even when they do nothing. In Python, this is considered "goofy" (in Alex Martelli's words):

```python
# Pythonic
item.weight = 5

# Un-Pythonic (Java-esque)
item.set_weight(item.get_weight() + 1)
```

The Python philosophy is to start with plain public attributes. If you later need validation or computation, convert to a property without breaking existing code. This is safe precisely because properties are overriding descriptors that intercept attribute access at the class level.

## The Repetition Problem

If both `weight` and `price` need the same "must be greater than zero" validation, you end up duplicating nearly identical getter/setter pairs. This violates DRY and is the motivation for property factories (see [[property-factory]]) and, ultimately, descriptors (Chapter 23).

## Connections

- Property factories eliminate repetitive validation code: [[property-factory]].
- Attribute deletion via properties and `__delattr__`: [[attribute-deletion]].
- The descriptor protocol underlying properties: [[descriptor-protocol]].
- Properties as overriding descriptors that shadow instance attributes: [[computed-properties]].
