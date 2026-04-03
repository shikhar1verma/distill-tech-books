---
title: "Handling Attribute Deletion"
book: "Fluent Python"
chapter: 22
tags: [python, property, deleter, del, metaprogramming]
related:
  - "[[property-for-validation]]"
  - "[[essential-attribute-builtins]]"
  - "[[computed-properties]]"
---

# Handling Attribute Deletion

> **The `@my_property.deleter` decorator (or `fdel` argument to `property()`) defines custom behavior for `del obj.attr`. The lower-level `__delattr__` special method provides an alternative interception point. Attribute deletion is rare in practice but completes the property protocol.**

## Deleting Plain Attributes

Python's `del` statement can remove attributes from objects, not just variables:

```python
class Demo:
    pass

d = Demo()
d.color = 'green'
print(d.color)    # 'green'
del d.color
print(d.color)    # AttributeError
```

This simply removes the `'color'` key from `d.__dict__`. No special methods are involved unless the class defines `__delattr__`.

## Property Deleters

The `property` protocol has three slots: `fget`, `fset`, and `fdel`. The `@property.deleter` decorator fills the `fdel` slot:

```python
class BlackKnight:
    def __init__(self):
        self.phrases = [
            ('an arm', "'Tis but a scratch."),
            ('another arm', "It's just a flesh wound."),
            ('a leg', "I'm invincible!"),
            ('another leg', "All right, we'll call it a draw."),
        ]

    @property
    def member(self):
        if self.phrases:
            return self.phrases[0][0]
        return 'nothing left!'

    @member.deleter
    def member(self):
        if self.phrases:
            member, text = self.phrases.pop(0)
            print(f'BLACK KNIGHT (loses {member}) -- {text}')
```

Usage:

```python
>>> knight = BlackKnight()
>>> knight.member
'an arm'
>>> del knight.member
BLACK KNIGHT (loses an arm) -- 'Tis but a scratch.
>>> del knight.member
BLACK KNIGHT (loses another arm) -- It's just a flesh wound.
```

The `del knight.member` statement triggers the deleter function, which pops the first phrase from the list. The property's getter then returns the next member.

### Classic Syntax

The same can be achieved with the `property()` constructor:

```python
member = property(member_getter, fdel=member_deleter)
```

Or with all three slots:

```python
member = property(fget=member_getter, fset=member_setter, fdel=member_deleter)
```

## The `__delattr__` Special Method

For lower-level control, implement `__delattr__` on the class. It is called on **every** `del obj.attr` statement, regardless of whether a property is involved:

```python
class Protected:
    def __init__(self):
        self.x = 10
        self.y = 20

    def __delattr__(self, name):
        if name == 'x':
            raise AttributeError("Cannot delete 'x'")
        super().__delattr__(name)  # default deletion for other attrs
```

```python
>>> p = Protected()
>>> del p.y    # works fine
>>> del p.x    # AttributeError: Cannot delete 'x'
```

Important: if a class implements `__delattr__`, it takes over deletion for **all** attributes. If a property with an `fdel` exists on the same class, `__delattr__` is called instead, and the property's deleter is **never invoked**. This mirrors how `__setattr__` takes precedence over property setters.

## When Deletion is Useful

Attribute deletion is uncommon in day-to-day Python. The main use cases:

1. **Clearing a `cached_property` cache.** Since `functools.cached_property` stores values as instance attributes, `del obj.cached_attr` clears the cache, forcing recomputation on the next access.

2. **Resource cleanup.** A deleter can release external resources (file handles, network connections) when an attribute is removed.

3. **Sentinel patterns.** Deleting an attribute can signal a state change, like marking a configuration as "not yet set."

4. **Testing and debugging.** Removing an attribute to verify fallback behavior or default values.

## The Complete Property Protocol

The three operations on a property correspond to three protocol slots:

| Operation | Decorator | Constructor Arg | Special Method |
|---|---|---|---|
| Read: `obj.attr` | `@property` | `fget` | `__get__` |
| Write: `obj.attr = val` | `@attr.setter` | `fset` | `__set__` |
| Delete: `del obj.attr` | `@attr.deleter` | `fdel` | `__delete__` |

Any slot left as `None` causes the corresponding operation to raise `AttributeError`.

At the descriptor level (Chapter 23), these map to `__get__`, `__set__`, and `__delete__` methods on the descriptor object. A property is simply a high-level API for creating descriptors with these methods.

## Connections

- Property getters and setters for validation: [[property-for-validation]].
- The `__delattr__` special method is part of the broader attribute handling API: [[essential-attribute-builtins]].
- `cached_property` relies on deletion to clear its cache: [[caching-properties]].
- The descriptor protocol that underlies properties, including `__delete__`: [[descriptor-protocol]].
