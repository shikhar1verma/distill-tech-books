---
title: "Metaclasses: __new__, __init__, and __prepare__"
slug: metaclasses
chapter: 24
book: fluent-python
type: code-heavy
depends_on:
  - import-time-vs-runtime
tags:
  - python
  - metaprogramming
  - metaclass
  - type
  - __prepare__
  - __slots__
---

# Metaclasses: `__new__`, `__init__`, and `__prepare__`

## Core Idea

A metaclass is a class whose instances are classes. By default, every Python class is an instance of `type`. A custom metaclass inherits from `type` and overrides `__new__` (and optionally `__prepare__`) to customize class creation. Metaclasses are the most powerful -- and most complex -- class metaprogramming tool.

## The `object`/`type` Relationship

```
object  <--subclass-- type
type    --instance--> object   (object is an instance of type)
type    --instance--> type     (type is an instance of itself)
```

- Every class is a **subclass** of `object`
- Every class is an **instance** of `type` (or a custom metaclass)
- A metaclass is a **subclass** of `type`

`abc.ABCMeta` is the metaclass for abstract base classes. `Iterable` is an instance of `ABCMeta`, which is itself an instance of `type`.

## Key Methods

### `__prepare__(meta_cls, cls_name, bases)`

- A `@classmethod` on the metaclass
- Called **before** the class body executes
- Returns the mapping object used as the class namespace
- Default: returns a regular `dict`
- Creative use: return a custom mapping to intercept attribute creation

### `__new__(meta_cls, cls_name, bases, cls_dict)`

- Called **after** the class body executes, with the populated namespace
- Can inspect and modify `cls_dict` before passing it to `type.__new__`
- This is the **only** place to dynamically configure `__slots__`
- Must call `super().__new__(meta_cls, cls_name, bases, cls_dict)` and return the result

### `__init__(cls, cls_name, bases, cls_dict)`

- Called after `__new__` returns
- Receives the already-created class as `cls`
- Used for post-creation setup (less common than `__new__`)

## The `MetaBunch` Example

A clean metaclass that auto-configures `__slots__` from class attributes:

```python
class MetaBunch(type):
    def __new__(meta_cls, cls_name, bases, cls_dict):
        defaults = {}
        new_dict = dict(__slots__=[], __init__=..., __repr__=...)

        for name, value in cls_dict.items():
            if name.startswith('__') and name.endswith('__'):
                if name not in new_dict:
                    new_dict[name] = value
            else:
                new_dict['__slots__'].append(name)
                defaults[name] = value

        return super().__new__(meta_cls, cls_name, bases, new_dict)

class Bunch(metaclass=MetaBunch):
    pass

class Point(Bunch):
    x = 0.0
    y = 0.0
```

`MetaBunch.__new__` intercepts the class namespace, moves user-defined attributes into `__slots__` with defaults, and injects `__init__` and `__repr__`.

## The `AutoConst` Hack with `__prepare__`

A creative combination of `__prepare__` and `__missing__`:

```python
class WilyDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__next_value = 0

    def __missing__(self, key):
        if key.startswith('__') and key.endswith('__'):
            raise KeyError(key)
        self[key] = value = self.__next_value
        self.__next_value += 1
        return value

class AutoConstMeta(type):
    def __prepare__(name, bases, **kwargs):
        return WilyDict()

class AutoConst(metaclass=AutoConstMeta):
    pass

class Flavor(AutoConst):
    banana      # 0
    coconut     # 1
    vanilla     # 2
```

When Python looks up bare names in the class body, `WilyDict.__missing__` auto-assigns incrementing integers.

## The `CheckedMeta` Example

For the `Checked` pattern with `__slots__`:

```python
class CheckedMeta(type):
    def __new__(meta_cls, cls_name, bases, cls_dict):
        if '__slots__' not in cls_dict:
            slots = []
            for name, constructor in cls_dict.get('__annotations__', {}).items():
                field = Field(name, constructor)
                cls_dict[name] = field
                slots.append(field.storage_name)
            cls_dict['__slots__'] = slots
        return super().__new__(meta_cls, cls_name, bases, cls_dict)
```

This metaclass reads `__annotations__` from `cls_dict` (the class does not exist yet, so `get_type_hints()` cannot be used), creates `Field` descriptors, and configures `__slots__` -- all before `type.__new__` builds the class.

## Connections

- [[classes-as-objects]] -- metaclasses inherit from `type`, the default class factory
- [[import-time-vs-runtime]] -- `__prepare__` and `__new__` execute at import time
- [[when-to-use-metaclasses]] -- guidance on when metaclasses are actually warranted
- [[init-subclass]] -- simpler alternative for most use cases
- [[class-decorators]] -- another simpler alternative
