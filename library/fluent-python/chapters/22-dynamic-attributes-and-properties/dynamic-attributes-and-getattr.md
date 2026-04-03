---
title: "Dynamic Attributes with __getattr__"
book: "Fluent Python"
chapter: 22
tags: [python, getattr, dynamic-attributes, metaprogramming, data-model]
related:
  - "[[computed-properties]]"
  - "[[essential-attribute-builtins]]"
  - "[[descriptor-protocol]]"
---

# Dynamic Attributes with `__getattr__`

> **`__getattr__` is Python's fallback mechanism for attribute access -- it is called only when normal lookup through the instance, class, and superclass chain has failed.**

## The Attribute Lookup Chain

When you write `obj.name`, Python follows a specific sequence:

1. Look in `type(obj).__dict__` (and its MRO) for a **data descriptor** (like a property) with that name.
2. Look in `obj.__dict__` for an instance attribute.
3. Look in `type(obj).__dict__` (and its MRO) for a **non-data descriptor** or plain class attribute.
4. If all of the above fail, call `type(obj).__getattr__(obj, 'name')` if it exists.
5. Otherwise, raise `AttributeError`.

This means `__getattr__` is a **fallback**, not a universal interceptor. It is only invoked when Python has exhausted all normal avenues. This is what makes it safe and efficient -- attributes that exist are accessed at full speed without any overhead from your custom logic.

Contrast this with `__getattribute__`, which is called on **every single** attribute access and is much harder to use correctly.

## Building FrozenJSON: Dot-Notation for Nested Dicts

A classic use case for `__getattr__` is wrapping JSON data so you can traverse nested dicts with dot notation instead of bracket syntax. The `FrozenJSON` class from the chapter demonstrates this:

```python
from collections import abc

class FrozenJSON:
    """Read-only facade for navigating JSON-like data with dot notation."""

    def __init__(self, mapping):
        self.__data = dict(mapping)

    def __getattr__(self, name):
        try:
            return getattr(self.__data, name)  # delegate dict methods
        except AttributeError:
            return FrozenJSON.build(self.__data[name])

    def __dir__(self):
        return self.__data.keys()

    @classmethod
    def build(cls, obj):
        if isinstance(obj, abc.Mapping):
            return cls(obj)
        elif isinstance(obj, abc.MutableSequence):
            return [cls.build(item) for item in obj]
        else:
            return obj
```

The critical design decisions here:

- **`self.__data`** uses name mangling (stored as `_FrozenJSON__data`) to avoid conflicts with keys in the JSON data. Regular names like `self.data` could collide with a JSON key called `"data"`.
- **`getattr(self.__data, name)`** is tried first, so dict methods like `.keys()` and `.items()` work transparently.
- **`build()`** recursively converts nested mappings and lists, but passes through scalars unchanged.
- **`__dir__`** returns the keys, enabling tab-completion in interactive environments.

## Handling Invalid Attribute Names

JSON keys may not be valid Python identifiers. The `keyword` module and `str.isidentifier()` help detect and fix these:

```python
import keyword

def __init__(self, mapping):
    self.__data = {}
    for key, value in mapping.items():
        if keyword.iskeyword(key):
            key += '_'       # "class" -> "class_"
        self.__data[key] = value
```

This transforms `student.class_` into a valid access for a key originally named `"class"`.

## Flexible Object Creation with `__new__`

The `build()` classmethod logic can alternatively be placed in `__new__`, which is the actual constructor (while `__init__` is just the initializer). When `__new__` returns an object that is not an instance of the class, Python skips calling `__init__`:

```python
class FrozenJSON:
    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)     # normal instance
        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]  # list, not FrozenJSON
        else:
            return arg                       # scalar, not FrozenJSON
```

This is Python's equivalent of a factory constructor -- the class call itself becomes polymorphic.

## Pitfalls and Best Practices

**`__getattr__` should raise `AttributeError` for missing keys.** The basic FrozenJSON raises `KeyError` when a key is not found, which violates the protocol. Production code should catch `KeyError` and re-raise as `AttributeError`.

**Attribute shadowing risk.** When creating instance attributes from data, a JSON key like `"keys"` or `"items"` could shadow dict methods. The FrozenJSON approach of delegating to the underlying dict's own attributes first mitigates this partially, but the risk remains in `Record`-style classes that write directly to `__dict__`.

**Performance.** `__getattr__` adds zero overhead for attributes that exist normally. It only fires on misses, making it efficient for wrapping patterns where most accesses hit the instance or class dict.

## Connections

- Properties (see [[computed-properties]]) are the higher-level way to add computed attributes and are implemented as overriding descriptors that take precedence over `__getattr__`.
- The built-in functions `getattr()`, `hasattr()`, and `dir()` all interact with `__getattr__` (see [[essential-attribute-builtins]]).
- Chapter 23 reveals that properties and `cached_property` are both descriptors, which operate at a different level of the attribute lookup chain than `__getattr__`.
