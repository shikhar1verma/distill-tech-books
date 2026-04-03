---
title: "Class Factory Functions"
slug: class-factory-functions
chapter: 24
book: fluent-python
type: code-heavy
depends_on:
  - classes-as-objects
tags:
  - python
  - metaprogramming
  - factory-pattern
  - type
  - __slots__
---

# Class Factory Functions

## Core Idea

A class factory is a regular function that creates and returns a new class by calling `type(name, bases, dict)`. This is the same mechanism Python uses internally when processing a `class` statement. The standard library's `collections.namedtuple` is the best-known class factory.

## The `record_factory` Example

The chapter builds `record_factory` -- a simplified, mutable alternative to `namedtuple`:

```python
def record_factory(cls_name: str, field_names) -> type:
    slots = parse_identifiers(field_names)

    def __init__(self, *args, **kwargs):
        attrs = dict(zip(self.__slots__, args))
        attrs.update(kwargs)
        for name, value in attrs.items():
            setattr(self, name, value)

    def __iter__(self):
        for name in self.__slots__:
            yield getattr(self, name)

    def __repr__(self):
        values = ', '.join(
            f'{name}={value!r}'
            for name, value in zip(self.__slots__, self)
        )
        return f'{self.__class__.__name__}({values})'

    cls_attrs = dict(
        __slots__=slots,
        __init__=__init__,
        __iter__=__iter__,
        __repr__=__repr__,
    )
    return type(cls_name, (object,), cls_attrs)
```

Usage:

```python
Dog = record_factory('Dog', 'name weight owner')
rex = Dog('Rex', 30, 'Bob')
# Dog(name='Rex', weight=30, owner='Bob')
```

## How It Works

1. `parse_identifiers` turns a space-separated string into a tuple of valid identifiers
2. Helper functions (`__init__`, `__iter__`, `__repr__`) are defined as closures that reference `__slots__`
3. A dict of class attributes is assembled, including `__slots__`
4. `type(cls_name, (object,), cls_attrs)` builds and returns the new class

## Why `__slots__`?

Using `__slots__` in the factory-built class:
- Restricts instances to declared attributes only (no `__dict__`)
- Saves memory when creating millions of instances
- Provides the attribute names in a known order for `__iter__` and `__repr__`

## Limitations

- Instances of factory-built classes are not pickle-serializable by default
- The class has no relationship to the factory function (its `__mro__` shows only `object`)

## Connections

- [[classes-as-objects]] -- `type()` three-argument form is the foundation
- [[init-subclass]] -- a more modern approach using `class` statement syntax
- [[metaclasses]] -- the most powerful class-building tool, also using `type.__new__`
