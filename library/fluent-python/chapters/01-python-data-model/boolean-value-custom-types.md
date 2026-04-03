---
title: "Boolean Value of Custom Types"
book: "Fluent Python"
chapter: 1
tags: [python, data-model, bool, truthiness, falsy, truthy, len]
related:
  - "[[special-dunder-methods]]"
  - "[[numeric-type-emulation]]"
  - "[[sequence-protocol-french-deck]]"
---

## Summary

Python accepts any object in a boolean context (`if`, `while`, `and`, `or`, `not`). To determine truthiness, it applies `bool(x)`, which first tries `x.__bool__()`, then falls back to `x.__len__()` (returning `False` if zero). If neither method is defined, the object is always truthy. By implementing `__bool__` (or `__len__`), you control how your custom objects behave in conditional expressions.

## How It Works

### The Resolution Order

When Python needs to evaluate the truth value of an object `x`, it follows this protocol:

1. **`x.__bool__()`** -- If defined, call it. Must return `True` or `False`.
2. **`x.__len__()`** -- If `__bool__` is not defined but `__len__` is, call `__len__()`. Return `False` if the result is `0`, `True` otherwise.
3. **Default** -- If neither `__bool__` nor `__len__` is defined, the object is **always truthy**.

```python
class ZeroVector:
    """Has __bool__ -> uses it."""
    def __bool__(self):
        return False

class EmptyBag:
    """No __bool__, has __len__ -> uses __len__."""
    def __len__(self):
        return 0

class Widget:
    """No __bool__, no __len__ -> always truthy."""
    pass

bool(ZeroVector())  # False (via __bool__)
bool(EmptyBag())    # False (via __len__ returning 0)
bool(Widget())      # True  (default)
```

### The Vector Example

The Vector class from Chapter 1 implements `__bool__` based on its magnitude:

```python
import math

class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))
```

- `Vector(0, 0)` has magnitude 0.0, so `bool(abs(self))` is `bool(0.0)` which is `False`.
- `Vector(1, 0)` has magnitude 1.0, so `bool(1.0)` is `True`.

A faster alternative avoids the square root:
```python
def __bool__(self):
    return bool(self.x or self.y)
```

This works because Python's `or` returns the first truthy operand (or the last operand), and `bool()` then converts it. If both `x` and `y` are `0`, `or` returns `0`, and `bool(0)` is `False`.

### Built-in Truthiness Rules

For reference, here are the built-in objects that are falsy:

| Type | Falsy value |
|------|-------------|
| `NoneType` | `None` |
| `bool` | `False` |
| Numbers | `0`, `0.0`, `0j`, `Decimal(0)`, `Fraction(0, 1)` |
| Sequences | `''`, `()`, `[]` |
| Mappings | `{}` |
| Sets | `set()`, `frozenset()` |

All of these use either `__bool__` or `__len__` internally. An empty list is falsy because `list.__len__` returns `0`.

## In Practice

### Collections: Prefer `__len__`

If your class is a container or collection, you typically do not need to implement `__bool__` at all. Just implement `__len__`, and empty collections will naturally be falsy:

```python
class TaskQueue:
    def __init__(self):
        self._tasks = []

    def __len__(self):
        return len(self._tasks)

    def add(self, task):
        self._tasks.append(task)

q = TaskQueue()
if not q:
    print("No tasks!")  # works because __len__ returns 0
q.add("deploy")
if q:
    print("Tasks pending!")  # __len__ returns 1 -> truthy
```

### Non-collections: Implement `__bool__`

For objects that are not collections (like Vector), `__len__` does not make semantic sense. Implement `__bool__` explicitly:

```python
class Connection:
    def __init__(self, host):
        self.host = host
        self._connected = False

    def connect(self):
        self._connected = True

    def __bool__(self):
        return self._connected

conn = Connection("example.com")
if not conn:
    conn.connect()  # not connected yet -> falsy
```

### Boolean Context Operators

The `and` and `or` operators in Python do **not** return `True`/`False` -- they return one of their operands:

```python
# `or` returns the first truthy operand, or the last operand
0 or [] or "hello"     # "hello"
0 or [] or 0           # 0

# `and` returns the first falsy operand, or the last operand
1 and "yes" and 42     # 42
1 and "" and 42        # ""
```

This is why the explicit `bool()` conversion is needed in `__bool__` methods -- the method must return an actual `bool`, not just a truthy/falsy value.

## Common Pitfalls

1. **Returning a non-bool from `__bool__`.** The method must return `True` or `False`. Returning an int (other than 0/1) or any other type will raise `TypeError`.

2. **Assuming all objects are truthy.** Newcomers often write `if obj is not None:` when they mean `if obj:`. These are different -- `None`, `0`, `""`, and `[]` are all falsy. Be deliberate about which check you need.

3. **Implementing `__bool__` on a collection that has `__len__`.** If your class has `__len__`, you usually do not need `__bool__`. Adding `__bool__` that contradicts `__len__` (e.g., a non-empty container that is falsy) will confuse users.

4. **Forgetting the `bool()` wrapper.** Inside `__bool__`, if you compute a value that might be an int or float, wrap it in `bool()`:
   ```python
   # BAD: may return 0 (int), not False (bool)
   def __bool__(self):
       return self.x or self.y

   # GOOD: always returns bool
   def __bool__(self):
       return bool(self.x or self.y)
   ```

5. **Performance of `__bool__`.** Since `__bool__` may be called frequently in loops and conditionals, keep it fast. The simpler `bool(self.x or self.y)` is faster than `bool(abs(self))` because it avoids `math.hypot` and the square root.

## See Also

- [[special-dunder-methods]] -- How `__bool__` fits into the Python Data Model
- [[numeric-type-emulation]] -- The Vector class that uses `__bool__`
- [[sequence-protocol-french-deck]] -- Collections where `__len__` provides truthiness for free
