---
title: "Descriptor Usage Tips"
book: "Fluent Python"
chapter: 23
tags: [python, descriptors, best-practices, oop]
related:
  - "[[descriptor-protocol]]"
  - "[[overriding-vs-nonoverriding-descriptors]]"
  - "[[validated-descriptor-pattern]]"
  - "[[methods-are-descriptors]]"
---

# Descriptor Usage Tips

> **Practical guidelines for choosing between `property`, overriding, and nonoverriding descriptors, including patterns for read-only attributes, validation, and caching.**

## How It Works

Descriptors come in several flavors, and picking the right one depends on what you need:

### Use `property` to keep it simple

`property` creates an overriding descriptor with both `__get__` and `__set__` (even without a setter -- the default `__set__` raises `AttributeError`). For one-off managed attributes, `property` is the easiest choice:

```python
class Account:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("balance cannot be negative")
        self._balance = value
```

Switch to a custom descriptor class when the same logic repeats across multiple attributes or classes.

### Read-only descriptors require `__set__`

A descriptor with only `__get__` is nonoverriding. An instance attribute can shadow it:

```python
class BadReadOnly:
    def __get__(self, instance, owner):
        return 'constant'

class MyClass:
    attr = BadReadOnly()

obj = MyClass()
obj.attr = 'oops'  # shadows the descriptor -- no error raised!
```

For true read-only behavior, implement `__set__` that raises `AttributeError`:

```python
class ReadOnly:
    def __init__(self, value):
        self.value = value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.value

    def __set__(self, instance, value):
        raise AttributeError("read-only attribute")
```

### Validation descriptors can work with `__set__` only

When the storage attribute name matches the managed attribute name (guaranteed by `__set_name__`), you don't need `__get__`. Python's normal instance attribute lookup handles reads, which is faster since it skips the descriptor machinery:

```python
class Positive:
    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError(f'{self.name} must be positive')
        instance.__dict__[self.name] = value

class Product:
    price = Positive()
    quantity = Positive()
```

### Caching can be done efficiently with `__get__` only

A nonoverriding descriptor computes a value in `__get__` and stores it as an instance attribute. The instance attribute shadows the descriptor on subsequent reads, making cached access as fast as a regular attribute lookup:

```python
class CachedProperty:
    def __init__(self, func):
        self.func = func
        self.attr_name = func.__name__

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.func(instance)
        instance.__dict__[self.attr_name] = value
        return value
```

This is essentially what `functools.cached_property` does. Use the stdlib version in production.

### Nonspecial methods can be shadowed by instance attributes

Functions are nonoverriding descriptors. Assigning `obj.method_name = something` creates an instance attribute that hides the method. This doesn't affect special methods (`__repr__`, `__len__`, etc.) because the interpreter looks those up on the class, not the instance.

## In Practice

**When to use `property`**: You have one or two managed attributes on a single class. The logic is specific to that class and won't be reused.

**When to write a descriptor class**: You have the same validation or transformation logic on multiple attributes, potentially across multiple classes. Examples: numeric range checks, string format validation, type enforcement, lazy computation.

**When to use `functools.cached_property`**: You need lazy evaluation with caching. The value is expensive to compute and doesn't change after first access.

**When to use a metaclass or `__init_subclass__`**: You need to inspect or modify descriptor instances after the class is created -- for example, to auto-generate `__init__` based on descriptors. But prefer `__set_name__` when it's sufficient.

## Common Pitfalls

- **Overengineering simple cases**: Don't write a descriptor class for a single attribute on one class. `property` exists for a reason.
- **Creating instance attributes in `__init__` after `__init__` runs**: Storing attributes after object construction bypasses the key-sharing memory optimization for `__dict__`. Initialize all attributes in `__init__`.
- **Assuming descriptors work on instances**: Descriptors must be class attributes. Storing a descriptor instance as an instance attribute has no special effect -- it's just a regular object.

## See Also

- [[descriptor-protocol]] -- the full protocol with `__get__`, `__set__`, `__delete__`, and `__set_name__`
- [[overriding-vs-nonoverriding-descriptors]] -- the core distinction that drives these guidelines
- [[validated-descriptor-pattern]] -- the template method approach for reusable validation
- [[methods-are-descriptors]] -- why method shadowing works the way it does
