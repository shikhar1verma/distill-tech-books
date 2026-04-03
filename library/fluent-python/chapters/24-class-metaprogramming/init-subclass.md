---
title: "Customizing Subclasses with __init_subclass__"
slug: init-subclass
chapter: 24
book: fluent-python
type: code-heavy
depends_on:
  - classes-as-objects
tags:
  - python
  - metaprogramming
  - __init_subclass__
  - PEP-487
  - descriptors
---

# Customizing Subclasses with `__init_subclass__`

## Core Idea

`__init_subclass__` (introduced in Python 3.6 via PEP 487) is called on a parent class whenever a new subclass is defined. The first argument is the **new subclass** (not the class where the method is defined). This provides a clean, simple hook for validation, registration, or enhancement of subclasses -- without resorting to metaclasses.

## Signature and Behavior

```python
class Base:
    def __init_subclass__(subclass, **kwargs):
        super().__init_subclass__(**kwargs)
        # subclass is the newly created class
```

Key points:
- Despite looking like a classmethod, it does **not** use `@classmethod`
- The first argument is the **subclass**, not the class where the method lives
- Always call `super().__init_subclass__(**kwargs)` for cooperative inheritance
- Fires **after** `type.__new__` builds the class, so it cannot configure `__slots__`

## The `Checked` Example

The book builds a `Checked` base class that reads type hints from subclasses and installs `Field` descriptors for runtime type validation:

```python
class Checked:
    def __init_subclass__(subclass, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, constructor in get_type_hints(subclass).items():
            setattr(subclass, name, Field(name, constructor))

class Movie(Checked):
    title: str
    year: int
    box_office: float
```

When `Movie` is defined, `__init_subclass__` fires and replaces each type hint with a `Field` descriptor that:
- Calls the constructor (e.g., `int()`) to produce a default value when no argument is given
- Validates values by passing them through the constructor (e.g., `float('billions')` raises `ValueError`)

## Common Use Cases

1. **Subclass registration** -- maintain a registry of plugins or handlers
2. **Structural validation** -- ensure subclasses define required attributes
3. **Automatic enhancement** -- inject methods or descriptors into subclasses

## Limitation: Cannot Configure `__slots__`

`__slots__` is only effective if present in the namespace **before** `type.__new__` is called. Since `__init_subclass__` runs **after** the class is already built, it cannot add or modify `__slots__`. For that, you need a [[metaclasses|metaclass]].

## `__init_subclass__` Is Not a Typical Class Method

Unlike `@classmethod` where `cls` is the class the method belongs to, `__init_subclass__` receives the *newly defined subclass*. Naming the first parameter `subclass` (rather than `cls`) makes this distinction clear.

## Connections

- [[classes-as-objects]] -- `__init_subclass__` works because classes are objects that can be inspected and modified
- [[class-decorators]] -- achieves similar results without inheritance coupling
- [[import-time-vs-runtime]] -- `__init_subclass__` fires at import time during class definition
- [[metaclasses]] -- needed when `__init_subclass__` is not powerful enough (e.g., for `__slots__`)
