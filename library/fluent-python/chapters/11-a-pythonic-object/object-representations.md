---
slug: object-representations
title: "Object Representations: __repr__, __str__, __format__, __bytes__"
chapter: 11
book: fluent-python
type: code-heavy
depends_on: []
tags: [python, dunder-methods, string-representation, data-model]
---

# Object Representations: `__repr__`, `__str__`, `__format__`, `__bytes__`

## Summary

Python provides four special methods for converting objects to string or bytes representations. `__repr__` produces a developer-facing string shown in the console and debugger, ideally one that could recreate the object. `__str__` produces a user-facing string used by `print()` and `str()`. `__format__` is called by f-strings, `format()`, and `str.format()` to produce custom formatted output using the Format Specification Mini-Language. `__bytes__` returns a binary representation via `bytes()`. If you implement only one, choose `__repr__` -- Python falls back to it when `__str__` is missing.

## How It Works

### `__repr__` -- for developers

When you type an object name at the Python console, or a debugger displays it, Python calls `repr()`, which invokes `__repr__`. The convention is to return a string that looks like a valid constructor call:

```python
def __repr__(self):
    class_name = type(self).__name__
    return '{}({!r}, {!r})'.format(class_name, *self)
```

Two important details here. First, `type(self).__name__` is used instead of hardcoding the class name so subclasses inherit a correct `__repr__` without overriding. Second, `{!r}` applies `repr()` to each component, ensuring strings get quotes and floats show full precision.

### `__str__` -- for end users

Called by `print()` and `str()`. If `__str__` is not defined, Python falls back to `__repr__`. The user-facing format is typically cleaner:

```python
def __str__(self):
    return str(tuple(self))  # e.g., "(3.0, 4.0)"
```

### `__format__` -- configurable display

The Format Specification Mini-Language is extensible. Each class can define its own format codes. The method signature is `__format__(self, fmt_spec='')`, where `fmt_spec` is everything after the colon in an f-string or `format()` call.

For example, the `Vector2d` class in Chapter 11 supports standard float codes applied to each component, plus a custom `'p'` suffix for polar coordinates:

```python
def __format__(self, fmt_spec=''):
    if fmt_spec.endswith('p'):
        fmt_spec = fmt_spec[:-1]
        coords = (abs(self), self.angle())
        outer_fmt = '<{}, {}>'
    else:
        coords = self
        outer_fmt = '({}, {})'
    components = (format(c, fmt_spec) for c in coords)
    return outer_fmt.format(*components)
```

This allows `f"{v:.2f}"` for Cartesian and `f"{v:.3ep}"` for polar.

### `__bytes__` -- binary serialization

Returns a `bytes` object. For `Vector2d`, the typecode character is prepended so the binary can be decoded later:

```python
def __bytes__(self):
    return (bytes([ord(self.typecode)]) +
            bytes(array(self.typecode, self)))
```

## In Practice

- **Always implement `__repr__`**: It is the most universally useful representation method. Make it produce output that could ideally be passed to `eval()` to recreate the object.
- **`__str__` is optional**: Only implement it when the end-user display should differ from the developer display.
- **`__format__` is worth implementing for domain types**: Currency, vectors, timestamps, and scientific values all benefit from custom format codes. The standard library's `datetime` class is a good model -- it reuses `strftime` codes.
- **`__bytes__` is niche**: Implement it when your class needs binary serialization, such as network protocols or compact storage.
- **`__iter__` is a force multiplier**: Making your class iterable (via `__iter__`) simplifies both `__repr__` (use `*self` unpacking) and `__str__` (use `tuple(self)`).

## Common Pitfalls

1. **Hardcoding the class name in `__repr__`**: If you write `return f"Vector2d({self.x!r}, {self.y!r})"`, subclasses like `ShortVector2d` will incorrectly display as `Vector2d(...)`. Use `type(self).__name__` instead.

2. **Confusing `format_spec` with `field_name`**: In `f"{obj.mass:5.3e}"`, `obj.mass` is the field expression and `5.3e` is the format spec. Only the format spec reaches `__format__`.

3. **Forgetting fallback behavior**: If a class has no `__format__`, the inherited `object.__format__` returns `str(self)` for an empty format spec but raises `TypeError` for any non-empty format spec. Always implement `__format__` if users might put format codes after the colon.

4. **Returning non-string types**: In Python 3, `__repr__`, `__str__`, and `__format__` must return `str`. Only `__bytes__` returns `bytes`.

## See Also

- [[classmethod-vs-staticmethod]] -- Alternative constructors like `frombytes` that round-trip with `__bytes__`
- [[hashable-objects]] -- Requires consistent `__repr__` for debugging
- Chapter 1 of Fluent Python -- First introduction to the data model and `__repr__`/`__str__`
- Python docs: [Format Specification Mini-Language](https://docs.python.org/3/library/string.html#formatspec)
