---
slug: overriding-class-attributes
title: "Overriding Class Attributes"
chapter: 11
book: fluent-python
type: mixed
depends_on: []
tags: [python, class-attributes, inheritance, shadowing, idioms]
---

# Overriding Class Attributes

## Summary

In Python, class attributes serve as default values for instance attribute lookups. When you read `self.attr` and the instance has no attribute by that name, Python falls back to the class attribute. When you write `self.attr = value`, Python creates a new instance attribute that shadows the class attribute -- the class attribute remains unchanged. The idiomatic way to customize class-wide defaults is to create a subclass and override at the class level, rather than mutating the base class.

## How It Works

### The lookup chain

Python's attribute lookup follows a well-defined order:

1. **Instance `__dict__`** (or slot) -- checked first
2. **Class `__dict__`** -- checked if not found on instance
3. **Base classes** (following the MRO) -- checked if not found on the class

This means a class attribute like `typecode = 'd'` acts as a default for every instance. Each instance appears to have `typecode`, but the value actually lives on the class until an instance creates its own.

### Shadowing in action

```python
class Vector2d:
    typecode = 'd'  # 8-byte double

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def export_info(self):
        return f'typecode={self.typecode!r}'

v1 = Vector2d(1.1, 2.2)
v1.export_info()           # "typecode='d'" -- reads class attribute
v1.typecode = 'f'          # creates INSTANCE attribute
v1.export_info()           # "typecode='f'" -- reads instance attribute (shadow)
Vector2d.typecode           # 'd' -- class attribute unchanged
```

After `v1.typecode = 'f'`, the instance has its own `typecode` in `v1.__dict__`, which shadows the class attribute. Other instances and the class itself are unaffected.

### Mutating the class attribute directly

You can change the class attribute:

```python
Vector2d.typecode = 'f'  # now ALL instances without their own typecode see 'f'
```

This affects every existing and future instance that does not shadow the attribute. This is a global mutation and should be done cautiously.

### The idiomatic pattern: subclass to customize

Instead of mutating the base class, create a subclass:

```python
class ShortVector2d(Vector2d):
    typecode = 'f'  # 4-byte float

sv = ShortVector2d(1/11, 1/27)
repr(sv)            # "ShortVector2d(0.09090909090909091, 0.037037037037037035)"
len(bytes(sv))      # 9 (vs 17 for double)
Vector2d.typecode   # 'd' -- base class unchanged
```

This pattern is pervasive in Python frameworks. Django's class-based views, for example, use it extensively: you subclass a generic view and override class attributes like `model`, `template_name`, or `paginate_by`.

### Why `type(self).__name__` matters

The `__repr__` method in `Vector2d` uses `type(self).__name__` instead of hardcoding `"Vector2d"`:

```python
def __repr__(self):
    class_name = type(self).__name__
    return '{}({!r}, {!r})'.format(class_name, *self)
```

When `ShortVector2d` inherits this method, `type(self).__name__` returns `"ShortVector2d"`, producing the correct representation without any override needed. Hardcoding the class name would force every subclass to reimplement `__repr__`.

## In Practice

### Configuration via class attributes

Class attributes are ideal for configuration defaults:

```python
class Downloader:
    timeout = 30
    max_retries = 3
    user_agent = 'MyBot/1.0'

class AggressiveDownloader(Downloader):
    timeout = 5
    max_retries = 10
```

This is cleaner than passing configuration through `__init__` parameters when the values are truly class-wide defaults.

### Per-instance customization

Sometimes you want to customize a single instance:

```python
d = Downloader()
d.timeout = 60  # this specific downloader gets a longer timeout
```

This works because the instance attribute shadows the class attribute. The pattern is convenient but less explicit than subclassing -- use it sparingly and document the intent.

### Class attributes vs `__init__` parameters

Choose class attributes for values that:
- Apply uniformly to all instances of a class or subclass
- Rarely vary between instances
- Define "policy" rather than "state"

Choose `__init__` parameters for values that:
- Vary per instance
- Are essential to the object's identity
- Should appear in `__repr__`

### Interaction with `__slots__`

Class attributes and `__slots__` coexist peacefully because class attributes live on the class object, not on instances. A slotted class can still have `typecode = 'd'` as a class attribute. However, you cannot use `self.typecode = 'f'` to shadow it on a slotted instance (unless `'typecode'` is in `__slots__` or `'__dict__'` is in `__slots__`).

## Common Pitfalls

1. **Mutating a mutable class attribute through an instance**: If the class attribute is a mutable object (list, dict), `self.shared_list.append(item)` modifies the class-level object -- it does NOT create an instance attribute. Only assignment (`self.x = ...`) creates a shadow.

2. **Forgetting the shadow effect**: After `obj.typecode = 'f'`, deleting `del obj.typecode` removes the instance attribute, and `obj.typecode` falls back to the class attribute again. This can be surprising.

3. **Mutating the base class globally**: `Vector2d.typecode = 'f'` changes behavior for all instances. Prefer subclassing to avoid unintended side effects.

4. **Confusing class attribute declaration with instance attribute**: In the class body, `typecode = 'd'` creates a class attribute. Only assignments to `self.typecode` inside methods create instance attributes. This distinction trips up programmers coming from Java, where field declarations create instance variables.

5. **Not using `type(self)` for class-attribute reads in methods**: If a method reads `Vector2d.typecode` directly instead of `self.typecode`, it ignores both instance shadows and subclass overrides. Always read via `self` to respect the full lookup chain.

## See Also

- [[classmethod-vs-staticmethod]] -- `@classmethod` with `cls` argument respects the same subclass override pattern
- [[slots]] -- Interaction between class attributes and slotted instances
- Django documentation on class-based views -- a real-world framework that uses class attribute overriding extensively
- Python docs: [Class and Instance Variables](https://docs.python.org/3/tutorial/classes.html#class-and-instance-variables)
