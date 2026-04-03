---
slug: private-and-protected-attributes
title: "Private and Protected Attributes (Name Mangling)"
chapter: 11
book: fluent-python
type: theory-heavy
depends_on: []
tags: [python, name-mangling, encapsulation, conventions, private-attributes]
---

# Private and Protected Attributes (Name Mangling)

## Summary

Python has no `private` keyword. Instead, it relies on a naming convention backed by a simple interpreter mechanism: attributes prefixed with double underscores (`__attr`) are "name-mangled" -- the interpreter stores them as `_ClassName__attr` to prevent accidental override in subclasses. Attributes with a single underscore prefix (`_attr`) are "protected" by convention only; the interpreter does not enforce any access restrictions. This design reflects Python's philosophy of "consenting adults" -- safety from accidents, not security from malicious access.

## How It Works

### Name mangling (double underscore)

When the Python compiler encounters an attribute name with two or more leading underscores and at most one trailing underscore inside a class definition, it rewrites the name by prepending `_ClassName`:

```python
class Vector2d:
    def __init__(self, x, y):
        self.__x = float(x)  # stored as _Vector2d__x
        self.__y = float(y)  # stored as _Vector2d__y
```

You can verify this by inspecting the instance `__dict__`:

```python
v = Vector2d(3, 4)
v.__dict__  # {'_Vector2d__x': 3.0, '_Vector2d__y': 4.0}
```

The mangled name is accessible if you know the pattern:

```python
v._Vector2d__x  # 3.0 -- works, but don't do this in production
```

### Why mangling exists: subclass safety

The core purpose is preventing accidental attribute collisions in inheritance hierarchies:

```python
class Dog:
    def __init__(self):
        self.__mood = 'happy'  # stored as _Dog__mood

class Beagle(Dog):
    def __init__(self):
        super().__init__()
        self.__mood = 'excited'  # stored as _Beagle__mood, NOT _Dog__mood
```

Without mangling, `Beagle.__init__` would overwrite `Dog`'s `__mood`, breaking any method in `Dog` that depends on it. With mangling, each class gets its own namespace for double-underscore attributes.

### Single underscore convention

A single leading underscore (`_attr`) signals "internal use" to other programmers. The interpreter does not enforce this -- it is purely a social contract:

```python
class MyClass:
    def __init__(self):
        self._internal = 42  # "please don't touch from outside"
```

The only place where `_` has a technical effect is in module-level imports: `from mymod import *` does not import names starting with `_`. But explicit imports like `from mymod import _private_func` still work.

### What does NOT trigger mangling

- Names with only one leading underscore: `_x` (convention only)
- Names with two leading AND two trailing underscores: `__init__`, `__repr__` (these are dunder/special methods, never mangled)
- Names inside functions or at module level (mangling only happens inside `class` bodies)

## In Practice

### When to use double underscores

Use `__attr` when:
- You are writing a base class in a framework or library, and you genuinely need to prevent subclass collisions on internal attributes.
- You want to enforce read-only access when combined with `@property`, as in the hashable `Vector2d`.

Do NOT use `__attr`:
- As a general-purpose "private" marker. Single underscore `_attr` is the Pythonic default for internal attributes.
- When you control both the base class and all subclasses (no collision risk).

### The community debate

The Python community is split on double underscores. Ian Bicking (creator of pip and virtualenv) wrote: "Never, ever use two leading underscores. This is annoyingly private." He recommends explicit mangling (`_MyThing_blahblah`) when collision avoidance is needed, arguing it is transparent where double underscore is obscure.

Ramalho's position is pragmatic: use double underscores for the specific purpose of preventing subclass accidents, but prefer single underscores for everyday "internal" attributes.

### The "protected" misnomer

Some Python documentation refers to single-underscore attributes as "protected" (borrowing Java/C++ terminology). This is misleading because Python does not enforce any access restriction. The term is sometimes used informally, but it can confuse programmers coming from languages with actual access modifiers.

## Common Pitfalls

1. **Thinking double underscore means "truly private"**: Any code can access `obj._ClassName__attr`. Name mangling is a safety net against accidents, not a security mechanism.

2. **Using double underscores everywhere**: Overusing `__attr` makes debugging harder (attribute names in `__dict__` are mangled), serialization messier, and the code less readable. Reserve it for genuine subclass collision scenarios.

3. **Mangling in dynamically set attributes**: Mangling only happens at compile time inside class bodies. If you write `setattr(obj, '__x', 42)`, the name is stored as `__x` literally -- no mangling occurs.

4. **Expecting mangling to work in `__slots__`**: When you declare `__slots__ = ('__x', '__y')`, the slot names ARE mangled (they become `_ClassName__x`). This can be surprising when introspecting slots via `__slots__` vs. the actual descriptor names.

5. **Breaking serialization**: If you pickle or JSON-serialize an object with mangled attributes, the mangled names (`_Vector2d__x`) appear in the output, coupling the serialized form to the class name. Renaming the class breaks deserialization.

## See Also

- [[read-only-properties]] -- Combines `__attr` with `@property` for clean public access
- [[hashable-objects]] -- Uses private attributes to enforce immutability
- [[slots]] -- Interacts with name mangling when slot names have double underscores
- Ian Bicking, "Paste Style Guide" -- the counterargument against double underscores
- Python docs: [Private name mangling](https://docs.python.org/3/reference/expressions.html#atom-identifiers)
