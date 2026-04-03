---
title: "Essential Attributes and Functions for Attribute Handling"
book: "Fluent Python"
chapter: 22
tags: [python, getattr, setattr, hasattr, vars, dir, introspection, data-model]
related:
  - "[[dynamic-attributes-and-getattr]]"
  - "[[property-for-validation]]"
  - "[[computed-properties]]"
  - "[[descriptor-protocol]]"
---

# Essential Attributes and Functions for Attribute Handling

> **Python provides a complete toolkit for attribute introspection and metaprogramming: three special attributes (`__class__`, `__dict__`, `__slots__`), five built-in functions (`dir`, `getattr`, `hasattr`, `setattr`, `vars`), and five special methods (`__getattr__`, `__getattribute__`, `__setattr__`, `__delattr__`, `__dir__`).**

## Special Attributes

### `__class__`

A reference to the object's class. `obj.__class__` is equivalent to `type(obj)`. Python uses this to look up special methods -- it searches the class (via `__class__`), never the instance, when looking for dunder methods like `__repr__` or `__getattr__`.

```python
x = [1, 2, 3]
assert x.__class__ is type(x) is list
```

### `__dict__`

A mapping (usually a `dict`) that stores the writable attributes of an object or class. Instance attributes live in `instance.__dict__`, class attributes in `ClassName.__dict__`.

Key behaviors:
- Objects **with** `__dict__` can have arbitrary attributes added at any time.
- Writing to `__dict__` directly bypasses `__setattr__` and property setters -- a critical metaprogramming technique.
- `__dict__` itself is **not listed** by `dir()`, but its keys are.

### `__slots__`

A tuple of strings declared on a class, restricting which instance attributes are allowed. When `__slots__` is defined and `'__dict__'` is not in the tuple, instances do not get a `__dict__`, saving significant memory for classes with many instances.

```python
class Point:
    __slots__ = ('x', 'y')

p = Point()
p.x = 1
p.y = 2
p.z = 3  # AttributeError: 'Point' object has no attribute 'z'
```

Classes with `__slots__` cannot be used with `vars()` or `functools.cached_property` unless they also include `'__dict__'` in the slots.

## Built-in Functions

### `dir([object])`

Lists an "interesting" set of attribute names. Intended for interactive use, not comprehensive introspection.

- Without arguments: lists names in the current scope.
- With an object: lists attributes from the instance `__dict__`, the class, and superclasses.
- Custom output via `__dir__()` method.
- Does **not** list `__dict__` itself, `__mro__`, or `__bases__`.

```python
class Widget:
    def __dir__(self):
        return ['color', 'size', 'reset']  # custom listing
```

### `getattr(object, name[, default])`

Retrieves the attribute identified by `name` from `object`. If the attribute does not exist, it either raises `AttributeError` or returns `default` if provided.

The full lookup chain is invoked: `__getattribute__` -> class descriptors -> instance `__dict__` -> class `__dict__` -> `__getattr__`.

Common pattern for safe attribute access:

```python
speed = getattr(vehicle, 'max_speed', 0)  # 0 if attr missing
```

### `hasattr(object, name)`

Returns `True` if `getattr(object, name)` does not raise `AttributeError`. This means it triggers the full lookup chain, including `__getattr__` if defined. If `__getattr__` raises an exception other than `AttributeError`, `hasattr` will propagate it.

```python
if hasattr(obj, 'render'):
    obj.render()
```

### `setattr(object, name, value)`

Assigns `value` to the named attribute. Triggers `__setattr__` if defined. Can create new attributes or overwrite existing ones.

```python
for key, val in config.items():
    setattr(obj, key, val)  # dynamic attribute creation
```

### `vars([object])`

Returns `object.__dict__`. Unlike `dir()`, it gives you the actual attribute storage mapping.

- Without arguments: returns `locals()` (the local scope dict).
- Raises `TypeError` for objects without `__dict__` (e.g., `__slots__`-only instances).

```python
>>> vars(my_obj)
{'name': 'Alice', 'age': 30}
```

## Special Methods

### `__getattr__(self, name)`

**Fallback only.** Called when normal attribute lookup (through `__getattribute__`) fails. This is the safe hook for dynamic/virtual attributes. If `__getattr__` also fails, it should raise `AttributeError`.

See [[dynamic-attributes-and-getattr]] for detailed coverage.

### `__getattribute__(self, name)`

**Called on every attribute access.** This is the method that implements the full lookup chain. Overriding it is tricky and rarely needed -- use `__getattr__` instead unless you have a specific reason.

To avoid infinite recursion inside `__getattribute__`, use `super().__getattribute__(name)` or `object.__getattribute__(self, name)`.

### `__setattr__(self, name, value)`

**Called on every attribute assignment**, whether through `obj.attr = val` or `setattr()`. Unlike `__getattr__`, there is no "fallback-only" version -- `__setattr__` intercepts all writes.

To actually store the attribute, implementations must use either `super().__setattr__(name, value)` or `self.__dict__[name] = value`. Using `self.name = value` inside `__setattr__` causes infinite recursion.

```python
class Strict:
    _allowed = {'x', 'y'}

    def __setattr__(self, name, value):
        if name not in self._allowed:
            raise AttributeError(f'Cannot set {name!r}')
        super().__setattr__(name, value)
```

### `__delattr__(self, name)`

Called on `del obj.attr`. Same caveats as `__setattr__` -- if defined, it handles **all** attribute deletion, potentially overriding property deleters.

### `__dir__(self)`

Called by `dir()`. Return an iterable of strings representing the attribute names to display. Used to customize tab-completion in interactive environments.

## The Interaction Map

Understanding which special method fires in which situation:

| Action | Triggers |
|---|---|
| `obj.attr` (attr exists) | `__getattribute__` |
| `obj.attr` (attr missing) | `__getattribute__` -> `__getattr__` |
| `obj.attr = val` | `__setattr__` |
| `del obj.attr` | `__delattr__` |
| `dir(obj)` | `__dir__` |

**Bypassing all special methods:** Read or write `obj.__dict__[name]` directly. This skips descriptors, `__getattribute__`, `__setattr__`, and all property logic. It is the standard escape hatch for metaprogramming code.

## The Asymmetry

A critical asymmetry to remember:

- `__getattr__` is a **fallback** (only called on failure).
- `__setattr__` is **always called** (no fallback equivalent).

This means implementing `__setattr__` has a much higher risk of bugs and performance issues than `__getattr__`. The Python docs explicitly recommend using properties or descriptors over `__getattribute__` and `__setattr__` whenever possible.

## Connections

- `__getattr__` for building dynamic wrappers: [[dynamic-attributes-and-getattr]].
- Properties as the high-level API for computed and validated attributes: [[computed-properties]], [[property-for-validation]].
- Descriptors as the underlying mechanism for properties: [[descriptor-protocol]].
