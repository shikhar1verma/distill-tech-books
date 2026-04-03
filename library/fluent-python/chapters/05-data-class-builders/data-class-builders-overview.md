---
title: "Overview of Data Class Builders"
slug: data-class-builders-overview
chapter: 5
book: "Fluent Python"
type: mixed
depends_on: []
tags: [dataclass, namedtuple, NamedTuple, metaprogramming, boilerplate]
---

# Overview of Data Class Builders

Python provides three standard-library tools for building classes that are primarily collections of fields, eliminating the repetitive `__init__`/`__repr__`/`__eq__` boilerplate.

## The Three Builders

| Builder | Module | Since | Technique |
|---|---|---|---|
| `namedtuple` | `collections` | Python 2.6 | Factory function (returns tuple subclass) |
| `NamedTuple` | `typing` | Python 3.5 (class syntax 3.6) | Metaclass (returns tuple subclass) |
| `@dataclass` | `dataclasses` | Python 3.7 | Class decorator (modifies class in place) |

All three auto-generate `__init__`, `__repr__`, and `__eq__`. None depend on inheritance to do their work -- they use different metaprogramming techniques to inject methods and attributes into the class under construction.

## The Boilerplate Problem

A plain class requires each field to be mentioned three times in `__init__` alone:

```python
class Coordinate:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
```

This gives you a useless `__repr__` (just a memory address) and identity-based `__eq__` (comparing object IDs, not values).

## Feature Comparison

| Feature | `namedtuple` | `NamedTuple` | `@dataclass` |
|---|---|---|---|
| Mutable instances | No | No | Yes (default) |
| Class statement syntax | No | Yes | Yes |
| Construct dict | `x._asdict()` | `x._asdict()` | `dataclasses.asdict(x)` |
| Get field names | `x._fields` | `x._fields` | `[f.name for f in fields(x)]` |
| Get defaults | `x._field_defaults` | `x._field_defaults` | `[f.default for f in fields(x)]` |
| Get field types | N/A | `x.__annotations__` | `x.__annotations__` |
| New instance w/ changes | `x._replace(...)` | `x._replace(...)` | `dataclasses.replace(x, ...)` |
| New class at runtime | `namedtuple(...)` | `NamedTuple(...)` | `make_dataclass(...)` |

## When to Use Which

- **`namedtuple`** -- when you need a lightweight immutable record with no type hints, or need backward compatibility with older Python.
- **`NamedTuple`** -- when you want type annotations on an immutable record and prefer class-body syntax.
- **`@dataclass`** -- when you need mutable instances, field-level options, post-init processing, or more customization.

## See Also

- [[classic-named-tuples]] -- details on `collections.namedtuple`
- [[typed-named-tuples]] -- details on `typing.NamedTuple`
- [[dataclass-decorator-and-fields]] -- details on `@dataclass`
- [[type-hints-101]] -- how type annotations work in data class declarations
