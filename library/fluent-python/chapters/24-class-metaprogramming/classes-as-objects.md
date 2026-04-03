---
title: "Classes as Objects and type() as a Class Factory"
slug: classes-as-objects
chapter: 24
book: fluent-python
type: mixed
depends_on: []
tags:
  - python
  - metaprogramming
  - type
  - class-objects
---

# Classes as Objects and `type()` as a Class Factory

## Core Idea

In Python, classes are first-class objects -- instances of `type`. Because classes are objects, they can be created at runtime, passed as arguments, stored in data structures, and inspected. The `type` built-in is simultaneously Python's default metaclass and a class factory: calling `type(name, bases, dict)` constructs a new class, which is exactly what Python does internally when processing every `class` statement.

## Class Attributes in the Data Model

Every class has several special attributes defined by the Python Data Model:

| Attribute | Description |
|-----------|-------------|
| `cls.__name__` | Simple class name (string) |
| `cls.__qualname__` | Dotted path from module scope to the class (e.g., `Outer.Inner`) |
| `cls.__bases__` | Tuple of direct base classes |
| `cls.__mro__` | Method Resolution Order tuple |
| `cls.__subclasses__()` | List of direct subclasses currently in memory (uses weak references) |
| `cls.__dict__` | The class namespace (a `mappingproxy`) |

None of these are listed by `dir()`.

## `type` as a Metaclass

`type` serves double duty:
1. **With one argument** -- `type(obj)` returns `obj.__class__`
2. **With three arguments** -- `type(name, bases, dict)` creates a new class

```python
# These two are equivalent:
class MyClass(Base):
    x = 42

MyClass = type('MyClass', (Base,), {'x': 42})
```

Every class is an instance of `type`, and `type` is its own metaclass (`type(type)` is `type`). The relationship between `object` and `type` is unique: `object` is an instance of `type`, and `type` is a subclass of `object`.

## Key Relationships

- Every class is a **subclass** of `object`
- Every class is an **instance** of `type` (or a custom metaclass)
- `type` is both a subclass of `object` and an instance of itself

## Connections

- [[class-factory-functions]] -- uses `type()` to build classes dynamically
- [[metaclasses]] -- custom metaclasses inherit from `type`
- [[init-subclass]] -- a simpler alternative to metaclasses for customizing subclasses
