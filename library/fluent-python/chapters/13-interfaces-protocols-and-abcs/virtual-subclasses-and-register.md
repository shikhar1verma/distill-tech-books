---
title: "Virtual Subclasses and register"
chapter: 13
slug: virtual-subclasses-and-register
type: code-heavy
depends_on:
  - goose-typing-and-abcs
  - defining-and-subclassing-abcs
tags:
  - virtual-subclass
  - register
  - subclasshook
  - isinstance
  - MRO
---

# Virtual Subclasses and register

An essential feature of goose typing is the ability to **register** a class as a virtual subclass of an ABC, even if it does not inherit from that ABC. The registered class passes `isinstance`/`issubclass` checks but inherits **nothing** from the ABC.

## How register Works

```python
@Tombola.register
class TomboList(list):
    def pick(self):
        if self:
            position = randrange(len(self))
            return self.pop(position)
        else:
            raise LookupError('pop from empty TomboList')

    load = list.extend

    def loaded(self):
        return bool(self)

    def inspect(self):
        return tuple(self)
```

### What register gives you

```python
issubclass(TomboList, Tombola)  # True
isinstance(TomboList(range(5)), Tombola)  # True
```

### What register does NOT give you

```python
TomboList.__mro__
# (<class 'TomboList'>, <class 'list'>, <class 'object'>)
# Tombola is NOT in the MRO -- no methods inherited
```

**Virtual subclasses are not checked for conformance at any time**, not even at instantiation. If you register a class that does not actually implement the ABC's interface, Python will believe you -- until something breaks at runtime.

## Two Syntaxes for register

### As a decorator (Python 3.3+)

```python
@SomeABC.register
class MyClass:
    ...
```

### As a function call

```python
class MyClass:
    ...

SomeABC.register(MyClass)
```

The function-call form is essential for registering **third-party classes** you don't control. The standard library uses this extensively:

```python
# In collections.abc source code:
Sequence.register(tuple)
Sequence.register(str)
Sequence.register(range)
Sequence.register(memoryview)
```

## __subclasshook__: Structural Recognition

Some ABCs implement `__subclasshook__` to recognize classes **structurally** -- without any registration or inheritance.

```python
class Struggle:
    def __len__(self): return 23

isinstance(Struggle(), abc.Sized)  # True -- no registration needed!
```

### How it works

`abc.Sized.__subclasshook__` checks if the candidate class (or any class in its MRO) has `__len__` in its `__dict__`. If so, it returns `True`.

```python
@classmethod
def __subclasshook__(cls, C):
    if cls is Sized:
        if any("__len__" in B.__dict__ for B in C.__mro__):
            return True
    return NotImplemented
```

### Why most ABCs don't have __subclasshook__

`__subclasshook__` only works reliably for ABCs with a **single special method** (like `Sized` with `__len__`). For more complex ABCs:

- Mappings implement `__len__`, `__getitem__`, and `__iter__` -- but so might non-mapping sequences. Checking just method names would produce false positives.
- `abc.Sequence` intentionally does **not** implement `__subclasshook__`.

**Advice:** Do not implement `__subclasshook__` in your own ABCs unless they define a single, unambiguous special method.

## When to Use register

| Scenario | Technique |
|---|---|
| You control the class | Subclass the ABC directly |
| You don't control the class (third-party) | Use `ABC.register(ThirdPartyClass)` |
| You want structural recognition | Implement `__subclasshook__` (rarely needed) |

## Caveats

1. **No conformance checking.** Python trusts your registration blindly.
2. **Static type checkers don't support register.** Mypy issue #2922 tracks this.
3. **No method inheritance.** The virtual subclass must implement everything itself.
4. **MRO is unaffected.** The ABC does not appear in `__mro__`.

## See Also

- [[goose-typing-and-abcs]] -- the goose typing philosophy
- [[defining-and-subclassing-abcs]] -- the traditional subclassing approach
- [[static-protocols-typing-protocol]] -- structural typing without registration
