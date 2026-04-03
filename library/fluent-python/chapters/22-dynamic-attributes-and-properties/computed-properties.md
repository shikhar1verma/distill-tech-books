---
title: "Computed Properties and Linked Record Retrieval"
book: "Fluent Python"
chapter: 22
tags: [python, property, computed-attributes, oop, data-model]
related:
  - "[[dynamic-attributes-and-getattr]]"
  - "[[caching-properties]]"
  - "[[property-for-validation]]"
  - "[[descriptor-protocol]]"
---

# Computed Properties and Linked Record Retrieval

> **The `@property` decorator turns a method into a read-only computed attribute, following Bertrand Meyer's Uniform Access Principle: the caller cannot tell whether `obj.attr` reads stored data or triggers a computation.**

## The `@property` Decorator

At its simplest, `@property` replaces a method with a read-only attribute:

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        import math
        return math.pi * self.radius ** 2
```

Now `c.area` looks like a plain attribute but computes its value every time. There is no setter, so `c.area = 100` raises `AttributeError`.

## Data-Driven Attribute Creation: The "Bunch" Idiom

Before we can demonstrate linked-record properties, we need a simple `Record` class. The "bunch" idiom creates attributes from keyword arguments by updating `self.__dict__` directly:

```python
class Record:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f'<{self.__class__.__name__} serial={self.serial!r}>'
```

This is concise and effective. Python's standard library offers similar classes: `types.SimpleNamespace`, `argparse.Namespace`, etc. The key insight is that `self.__dict__.update(kwargs)` is a fast way to create many instance attributes at once.

## Linking Records with Properties

Given flat data where events reference speakers and venues by serial numbers, properties can "dereference" these into actual objects -- similar to Django's ORM foreign key access:

```python
class Event(Record):
    @property
    def venue(self):
        key = f'venue.{self.venue_serial}'
        return self.__class__.fetch(key)

    @property
    def speakers(self):
        spkr_serials = self.__dict__['speakers']
        fetch = self.__class__.fetch
        return [fetch(f'speaker.{key}') for key in spkr_serials]
```

Two important details here:

1. **`self.__class__.fetch(key)`** instead of `self.fetch(key)`. If the data contained a key named `"fetch"`, it would shadow the class method on that specific instance. Using `self.__class__` guarantees we always reach the staticmethod.

2. **`self.__dict__['speakers']`** instead of `self.speakers`. The `speakers` property has the same name as the data field stored in the instance. Accessing `self.speakers` inside the property body would call the property again, causing infinite recursion. Reading from `__dict__` directly bypasses the descriptor protocol.

## Properties Override Instance Attributes

This is the most important rule to internalize: **properties are overriding descriptors, meaning they always take precedence over instance attributes of the same name.**

```python
class Demo:
    @property
    def prop(self):
        return 'computed'

obj = Demo()
obj.__dict__['prop'] = 'stored'  # write directly to instance dict
print(obj.prop)  # still prints 'computed' -- property wins!
```

When Python evaluates `obj.attr`:
1. It first checks `type(obj)` and its MRO for a **data descriptor** (a class with `__get__` and `__set__` or `__delete__`). Properties qualify.
2. Only if no data descriptor is found does it check `obj.__dict__`.

This explains why `self.__dict__['speakers']` is necessary in the `speakers` property -- the normal `self.speakers` path is intercepted by the property before the instance dict is ever consulted.

The only way to remove a property's override is to replace or delete it on the **class** itself:

```python
Demo.prop = 'no longer a property'  # destroys the property object
print(obj.prop)  # now reads 'stored' from obj.__dict__
```

## The `load()` Factory Pattern

The chapter's `load()` function demonstrates a clean pattern for building heterogeneous record collections:

```python
def load(path):
    records = {}
    for collection, raw_records in raw_data['Schedule'].items():
        record_type = collection[:-1]          # 'events' -> 'event'
        cls_name = record_type.capitalize()    # 'event' -> 'Event'
        cls = globals().get(cls_name, Record)  # look up class by name
        if inspect.isclass(cls) and issubclass(cls, Record):
            factory = cls
        else:
            factory = Record
        for raw in raw_records:
            key = f'{record_type}.{raw["serial"]}'
            records[key] = factory(**raw)
    return records
```

This automatically uses `Event` for event records while falling back to `Record` for everything else. New subclasses like `Speaker` or `Venue` would be picked up automatically.

## When to Use Computed Properties

Properties are ideal when:
- You want attribute-style access (`obj.venue`) but need to compute or dereference a value.
- You are migrating from a plain attribute to a computed one without breaking existing code.
- You need to enforce that an attribute is read-only.

Properties are less ideal when:
- The computation is expensive and needs caching (see [[caching-properties]]).
- You need the same validation on many attributes (see [[property-factory]]).
- You need full descriptor flexibility (see Chapter 23).

## Connections

- `__getattr__` (see [[dynamic-attributes-and-getattr]]) is the lower-level fallback; properties operate earlier in the lookup chain and take precedence.
- Caching computed values is covered in [[caching-properties]].
- Read/write properties for validation are explored in [[property-for-validation]].
