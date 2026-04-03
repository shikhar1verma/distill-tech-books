---
title: "Enhancing Classes with Class Decorators"
slug: class-decorators
chapter: 24
book: fluent-python
type: code-heavy
depends_on:
  - init-subclass
tags:
  - python
  - metaprogramming
  - decorators
  - dataclass
---

# Enhancing Classes with Class Decorators

## Core Idea

A class decorator is a callable that receives a class object, may inspect or modify it, and returns a class (usually the same one, enhanced). Class decorators are applied **after** the class body executes and after `__init_subclass__`, making them the last step of class construction before the name is bound.

```python
def my_decorator(cls: type) -> type:
    # inspect, modify, or replace cls
    return cls

@my_decorator
class MyClass:
    ...
```

The `@my_decorator` line is syntactic sugar for `MyClass = my_decorator(MyClass)`.

## Advantages Over `__init_subclass__`

- **No inheritance coupling**: the user's class does not need to inherit from a specific base
- **No metaclass conflicts**: decorators don't interfere with the metaclass hierarchy
- **Composable**: multiple decorators can be stacked

This is why `@dataclass` was implemented as a class decorator (PEP 557 cites this rationale explicitly).

## The `@checked` Decorator Example

The book reimplements the `Checked` functionality as a decorator:

```python
def checked(cls: type) -> type:
    for name, constructor in get_type_hints(cls).items():
        setattr(cls, name, Field(name, constructor))
    cls.__init__ = __init__       # inject methods
    cls.__repr__ = __repr__
    cls.__setattr__ = __setattr__
    return cls

@checked
class Movie:
    title: str
    year: int
    box_office: float
```

The decorator:
1. Reads type hints from the class
2. Replaces each annotated attribute with a `Field` descriptor
3. Injects `__init__`, `__repr__`, and `__setattr__` as instance methods
4. Returns the enhanced class

## Decorator vs. `__init_subclass__` -- When to Choose

| Criterion | `__init_subclass__` | Class Decorator |
|-----------|---------------------|-----------------|
| Requires inheritance | Yes | No |
| Applies to all subclasses automatically | Yes | No (each must be decorated) |
| Risk of metaclass conflict | Low | None |
| Timing | Before decorator | After `__init_subclass__` |

## Limitation: Cannot Configure `__slots__`

Like `__init_subclass__`, a class decorator runs **after** `type.__new__` has already built the class. It is too late to configure `__slots__`. For dynamic `__slots__`, you need a [[metaclasses|metaclass]].

## Connections

- [[init-subclass]] -- similar capability but requires inheritance
- [[import-time-vs-runtime]] -- decorators are applied at import time, after the class body and `__init_subclass__`
- [[metaclasses]] -- the only tool that can modify the class namespace *before* `type.__new__`
- [[when-to-use-metaclasses]] -- decorators replace many former metaclass use cases
