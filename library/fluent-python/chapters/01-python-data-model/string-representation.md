---
title: "String Representation: __repr__ vs __str__"
book: "Fluent Python"
chapter: 1
tags: [python, data-model, repr, str, string-representation, formatting]
related:
  - "[[special-dunder-methods]]"
  - "[[numeric-type-emulation]]"
  - "[[boolean-value-custom-types]]"
---

## Summary

Python provides two special methods for converting objects to strings: `__repr__` for an unambiguous developer-facing representation, and `__str__` for a readable end-user-facing representation. If you implement only one, choose `__repr__` -- the default `__str__` inherited from `object` falls back to calling `__repr__`.

## How It Works

### `__repr__`: The Developer View

`__repr__` is called by `repr()`, the interactive console, the debugger, and the `!r` conversion in f-strings. Its goal is to produce an **unambiguous** string, ideally one that looks like valid Python code to recreate the object:

```python
class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Vector({self.x!r}, {self.y!r})'

v = Vector(3, 4)
repr(v)          # 'Vector(3, 4)'
```

The `!r` inside the f-string applies `repr()` to the attribute values. This is crucial because it distinguishes `Vector(1, 2)` (numbers) from `Vector('1', '2')` (strings), which would behave differently.

### `__str__`: The User View

`__str__` is called by `str()` and `print()`. It should return a **readable** string aimed at end users:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point({self.x!r}, {self.y!r})'

    def __str__(self):
        return f'({self.x}, {self.y})'

p = Point(3, 4)
repr(p)    # 'Point(3, 4)'     -- for developers
str(p)     # '(3, 4)'          -- for users
print(p)   # (3, 4)            -- print calls __str__
```

### The Fallback Chain

When Python needs a string representation:

1. **`repr(obj)`** calls `type(obj).__repr__(obj)`. If not defined, uses `object.__repr__`, which gives `<ClassName object at 0x...>`.

2. **`str(obj)`** calls `type(obj).__str__(obj)`. If `__str__` is not defined on the class, `object.__str__` falls back to `__repr__`.

3. **`print(obj)`** calls `str(obj)`.

4. **f-strings**: `f'{obj}'` calls `str(obj)`; `f'{obj!r}'` calls `repr(obj)`; `f'{obj!s}'` explicitly calls `str(obj)`.

This fallback means that if you only define `__repr__`, `print()` and `str()` will use it too. But the reverse is not true -- if you only define `__str__`, the interactive console and `repr()` will still show `<ClassName object at 0x...>`.

### `__format__` and Format Specs

There is a third string method: `__format__`, called by `format()` and f-strings with format specs like `f'{obj:.2f}'`. This is covered in depth in Chapter 5. If not defined, Python falls back to `str(obj)`.

## In Practice

Here is the decision framework for which to implement:

| Situation | Implement |
|-----------|-----------|
| Quick data class / debugging | `__repr__` only |
| Object displayed to end users | Both `__repr__` and `__str__` |
| Numeric type needing format specs | `__repr__`, `__str__`, and `__format__` |

The `__repr__` string should ideally satisfy this test: if it looks like a constructor call, a developer should be able to copy-paste it to recreate the object. For example, `Vector(3, 4)` is a valid Python expression that creates the same Vector.

Standard library examples:
- `datetime.datetime(2024, 1, 15, 10, 30)` -- `__repr__` looks like constructor
- `'2024-01-15 10:30:00'` -- `__str__` is human-readable

### Programmers Coming from Java

If you have a Java background, you might be used to implementing `toString()`. The Python equivalent is `__str__`. But the advice in Fluent Python is clear: implement `__repr__` first. Java does not have a direct equivalent of `__repr__`, and many Python beginners skip it to their detriment.

## Common Pitfalls

1. **Implementing `__str__` but not `__repr__`.** This is the most common mistake. The interactive console and debuggers use `repr()`, so you will see `<MyClass object at 0x...>` where it matters most -- during debugging.

2. **`__repr__` that lies.** If `repr(obj)` returns `"Vector(3, 4)"` but `Vector(3, 4)` does not actually reconstruct the object (e.g., because the constructor has different parameters), that is misleading. If an exact reconstruction is not possible, use angle-bracket notation: `<Vector x=3, y=4>`.

3. **Not using `!r` in f-strings inside `__repr__`.** Without `!r`, string attributes will not be quoted:
   ```python
   # BAD:  f'Card({self.rank}, {self.suit})'  -> Card(7, diamonds)
   # GOOD: f'Card({self.rank!r}, {self.suit!r})' -> Card('7', 'diamonds')
   ```

4. **Infinite recursion.** If `__repr__` references an attribute that in turn references the original object, you get infinite recursion. This is common with bidirectional relationships. Use an ID or short form instead.

5. **Performance in `__repr__`.** Since `repr()` is called frequently during debugging and logging, avoid expensive computations inside `__repr__`. It should be fast and side-effect-free.

## See Also

- [[special-dunder-methods]] -- The broader framework of Python special methods
- [[numeric-type-emulation]] -- Uses `__repr__` in the Vector class
- [[boolean-value-custom-types]] -- Another behavioral special method
