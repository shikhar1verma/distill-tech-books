---
title: "Validated Descriptor Pattern"
book: "Fluent Python"
chapter: 23
tags: [python, descriptors, validation, design-patterns, oop]
related:
  - "[[descriptor-protocol]]"
  - "[[overriding-vs-nonoverriding-descriptors]]"
  - "[[descriptor-usage-tips]]"
---

# Validated Descriptor Pattern

> **An abstract base descriptor class delegates validation to a template method, letting concrete subclasses focus on their specific validation rules.**

## How It Works

When you need several descriptor types that share the same storage and naming logic but differ in validation, the **template method pattern** (also called self-delegation) avoids code duplication. You create an abstract base class that handles `__set_name__` and `__set__`, then calls an abstract `validate()` method. Each concrete subclass implements only `validate()`.

```python
import abc

class Validated(abc.ABC):
    """Abstract descriptor: subclasses implement validate()."""

    def __set_name__(self, owner, name):
        self.storage_name = name

    def __set__(self, instance, value):
        value = self.validate(self.storage_name, value)
        instance.__dict__[self.storage_name] = value

    @abc.abstractmethod
    def validate(self, name, value):
        """Return validated value or raise ValueError."""


class Quantity(Validated):
    """A number greater than zero."""

    def validate(self, name, value):
        if value <= 0:
            raise ValueError(f'{name} must be > 0')
        return value


class NonBlank(Validated):
    """A string with at least one non-space character."""

    def validate(self, name, value):
        value = value.strip()
        if not value:
            raise ValueError(f'{name} cannot be blank')
        return value  # returns cleaned value
```

The `validate()` method returns the validated (and possibly cleaned) value. This is deliberate: it gives subclasses a chance to normalize data. `NonBlank.validate()` strips whitespace before checking, so the stored value is always trimmed.

Using these descriptors in a managed class is clean:

```python
class LineItem:
    description = NonBlank()
    weight = Quantity()
    price = Quantity()

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price

    def subtotal(self):
        return self.weight * self.price
```

This looks almost like a Django model definition -- and that's no coincidence. Django model fields are descriptors that follow a similar pattern.

## In Practice

This pattern shines when you have a domain with many validated fields. Consider an e-commerce system:

```python
class PositiveInt(Validated):
    def validate(self, name, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError(f'{name} must be a positive integer')
        return value

class EmailAddress(Validated):
    def validate(self, name, value):
        if not isinstance(value, str) or '@' not in value:
            raise ValueError(f'{name} must be a valid email')
        return value.lower().strip()
```

Each new descriptor type is just a few lines. The `__set_name__`, `__set__`, and storage logic is written once in `Validated` and inherited by all.

The pattern also works well with frameworks. If you're building an ORM, form library, or configuration system, the `Validated` base class becomes part of your public API. Users subclass it to create custom field types without understanding descriptor internals.

Notice that no `__get__` is defined. Since `__set_name__` ensures the storage name matches the attribute name, Python's normal instance attribute lookup handles reads efficiently -- no descriptor overhead on every read.

## Common Pitfalls

- **Forgetting to return the value from `validate()`**: If `validate()` returns `None` implicitly, the stored value becomes `None`. Always return the validated value.
- **Mutating the value without returning it**: If you strip whitespace or convert types, you must return the modified value. The `__set__` method stores whatever `validate()` returns.
- **Making the ABC too rigid**: Keep the base class minimal. If some descriptors need `__get__` and others don't, don't force it into the ABC. Subclasses can add `__get__` as needed.

## See Also

- [[descriptor-protocol]] -- the `__get__`/`__set__`/`__set_name__` methods this pattern builds on
- [[overriding-vs-nonoverriding-descriptors]] -- why `Validated` subclasses are overriding descriptors
- [[descriptor-usage-tips]] -- when to use this pattern vs `property`
