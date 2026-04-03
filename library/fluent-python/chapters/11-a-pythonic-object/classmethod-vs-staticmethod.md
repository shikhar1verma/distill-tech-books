---
slug: classmethod-vs-staticmethod
title: "classmethod vs staticmethod"
chapter: 11
book: fluent-python
type: mixed
depends_on:
  - object-representations
tags: [python, decorators, classmethod, staticmethod, alternative-constructors]
---

# classmethod vs staticmethod

## Summary

`@classmethod` receives the class itself as its first argument (`cls`) and is the Pythonic way to define alternative constructors. `@staticmethod` receives no implicit first argument and behaves like a plain function that happens to live inside a class body. Ramalho argues that good use cases for `@staticmethod` are very rare -- a module-level function usually suffices.

## How It Works

### `@classmethod`

The decorator changes how the method is called: instead of receiving the instance (`self`), it receives the class (`cls`). This is crucial for alternative constructors because `cls` will be the actual subclass if called on a subclass, enabling proper inheritance.

```python
class Vector2d:
    typecode = 'd'

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(*memv)  # cls, not Vector2d!
```

The key line is `return cls(*memv)`. If a subclass `ShortVector2d(Vector2d)` calls `ShortVector2d.frombytes(data)`, `cls` is `ShortVector2d`, so the returned instance has the correct type. Hardcoding `Vector2d(*memv)` would break polymorphism.

### `@staticmethod`

A static method receives no special first argument. It is essentially a plain function namespaced inside the class:

```python
class Demo:
    @staticmethod
    def statmeth(*args):
        return args

Demo.statmeth('spam')  # ('spam',)
```

### Behavior comparison

```python
class Demo:
    @classmethod
    def klassmeth(*args):
        return args

    @staticmethod
    def statmeth(*args):
        return args

Demo.klassmeth()       # (<class 'Demo'>,)
Demo.klassmeth('spam') # (<class 'Demo'>, 'spam')
Demo.statmeth()        # ()
Demo.statmeth('spam')  # ('spam',)
```

No matter how you invoke `Demo.klassmeth`, the `Demo` class is always the first argument. `statmeth` receives nothing special.

## In Practice

### Alternative constructors (the primary use case for `@classmethod`)

The standard library is full of `@classmethod` alternative constructors:

- `dict.fromkeys(['a', 'b'], 0)` -- builds a dict from a key sequence
- `datetime.fromtimestamp(ts)` -- builds a datetime from a Unix timestamp
- `int.from_bytes(b'\x00\xff', 'big')` -- builds an int from bytes

The pattern is consistent: the classmethod parses some input format and calls `cls(...)` to construct the instance. This means subclasses automatically inherit working alternative constructors.

### When (if ever) to use `@staticmethod`

Ramalho's position is clear: "Good use cases for `staticmethod` are very rare." If a function does not need access to the class or instance, it can live as a module-level function. Placing it in the class as a `@staticmethod` only makes sense if the function is conceptually very tightly coupled to the class and you want it to be discoverable via the class namespace.

A common (but debatable) use case is validation helpers:

```python
class Temperature:
    @staticmethod
    def _celsius_to_fahrenheit(c):
        return c * 9 / 5 + 32
```

Even here, a plain function `_celsius_to_fahrenheit(c)` at module level would work fine.

### Inheritance behavior

`@classmethod` is inheritance-aware -- `cls` is the subclass when called on a subclass. `@staticmethod` has no class awareness at all. This is the decisive practical difference.

## Common Pitfalls

1. **Using `@staticmethod` for alternative constructors**: If you use `@staticmethod` and hardcode the class name, subclasses break. Always use `@classmethod` when the method needs to create instances.

2. **Forgetting `cls` is the class, not an instance**: Inside a classmethod you cannot access instance attributes. You can access class attributes via `cls.typecode`, and you can call `cls(...)` to create instances.

3. **Overusing `@staticmethod` to "organize" code**: Putting utility functions as static methods feels clean but couples callers to the class unnecessarily. Module-level functions are more Pythonic and easier to test.

4. **Not using `cls` to construct the return value**: Writing `return Vector2d(*args)` instead of `return cls(*args)` inside a classmethod defeats the purpose -- subclasses will get instances of the parent class.

## See Also

- [[object-representations]] -- `frombytes` is the alternative constructor that round-trips with `__bytes__`
- [[overriding-class-attributes]] -- Subclassing idiom that works hand-in-hand with `cls`-based classmethods
- Python docs: [classmethod](https://docs.python.org/3/library/functions.html#classmethod), [staticmethod](https://docs.python.org/3/library/functions.html#staticmethod)
- Julien Danjou, "The Definitive Guide on How to Use Static, Class or Abstract Methods in Python" -- a counterpoint to Ramalho's skepticism of `@staticmethod`
