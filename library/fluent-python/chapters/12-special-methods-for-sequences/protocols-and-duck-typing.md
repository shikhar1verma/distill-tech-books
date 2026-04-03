---
title: "Protocols and Duck Typing"
book: "Fluent Python"
chapter: 12
tags: [python, protocols, duck-typing, sequence-protocol, structural-subtyping, typing-protocol]
type: "theory-heavy"
depends_on: []
related:
  - "[[vector-multidimensional-sequence]]"
  - "[[sliceable-sequence-getitem]]"
  - "[[dynamic-protocols-and-duck-typing]]"
  - "[[special-dunder-methods]]"
  - "[[sequence-protocol-french-deck]]"
---

## Summary

A protocol in Python is an informal interface defined entirely by convention and documentation, not by code. The sequence protocol, for example, consists of just `__len__` and `__getitem__`. Any class that implements these two methods with the expected signatures and semantics *is* a sequence -- regardless of what it inherits from. This principle is called **duck typing**: if it quacks like a duck and walks like a duck, it is a duck. Python checks behavior, not lineage.

## How It Works

### The Sequence Protocol

The sequence protocol is deceptively simple. Implement two methods and your class gains indexing, slicing, iteration, `in` membership testing, `sorted()`, `reversed()`, and `random.choice()`:

```python
class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit)
                       for suit in self.suits
                       for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]
```

`FrenchDeck` inherits from `object` -- it does not subclass `list`, `tuple`, `Sequence`, or any abstract base class. Yet it behaves exactly like a sequence because it implements the right methods with the right behavior. An experienced Python programmer reads this code and immediately understands: this *is* a sequence.

### Partial Protocol Implementation

Protocols are informal and unenforced, so you can implement only the parts you need. For example, `__getitem__` alone is enough to support iteration. When Python encounters a `for` loop on an object without `__iter__`, it falls back to calling `__getitem__` with indices 0, 1, 2, ... until an `IndexError` is raised. You only need `__len__` if something actually calls `len()` on your object.

This pragmatism is a feature, not a defect. The Python Data Model documentation itself advises:

> When implementing a class that emulates any built-in type, it is important that the emulation only be implemented to the degree that it makes sense for the object being modeled.

### Duck Typing Defined

The term comes from Alex Martelli's 2000 post to `comp.lang.python`:

> Don't check whether it *is* a duck: check whether it *quacks* like a duck, *walks* like a duck, etc., depending on exactly what subset of duck-like behavior you need.

In practice, duck typing means:

1. **No type checks at call sites**: Functions accept any object that has the methods they need, without `isinstance()` guards.
2. **No mandatory base classes**: You never need to inherit from a framework class to participate in its protocols.
3. **Errors surface at method call time**: If an object does not quack correctly, you get an `AttributeError` or `TypeError` at the exact point where the missing behavior was needed -- not at some registration checkpoint.

### Dynamic Protocols vs Static Protocols

Python 3.8 introduced `typing.Protocol` (PEP 544), which adds **static protocol** checking to the language. A static protocol is a class that inherits from `typing.Protocol` and declares method signatures. Type checkers like mypy verify that a class conforms to the protocol without requiring inheritance:

```python
from typing import Protocol

class Sized(Protocol):
    def __len__(self) -> int: ...

def print_length(obj: Sized) -> None:
    print(len(obj))
```

Any class with a `__len__` method returning `int` satisfies `Sized` -- no inheritance needed. This is called **structural subtyping**, the static counterpart to duck typing.

Key differences between the two kinds of protocols:

| Aspect | Dynamic protocol | Static protocol (`typing.Protocol`) |
|--------|-----------------|--------------------------------------|
| Defined in | Documentation, convention | Code (class inheriting from `Protocol`) |
| Enforced by | Runtime (`AttributeError` on missing method) | Type checker (mypy, pyright) at analysis time |
| Partial implementation | Allowed (implement only what you need) | Must implement all declared methods |
| Introduced | Python 1.x (always existed) | Python 3.8 (PEP 544) |

Both coexist in modern Python. Dynamic protocols remain the dominant pattern in runtime code, while static protocols provide safety nets during development.

## In Practice

### Recognizing Protocols in the Wild

Python documentation often signals protocols with phrases like "a file-like object" or "a mapping-like object." These are shorthand for "something that implements the relevant subset of the file/mapping protocol." When you see these phrases, think: "What methods does this thing need to have?"

Common Python protocols:

| Protocol | Required methods | Unlocks |
|----------|-----------------|---------|
| Iterable | `__iter__` (or `__getitem__` fallback) | `for`, unpacking, `list()`, `set()` |
| Sequence | `__len__` + `__getitem__` | Indexing, slicing, `in`, `sorted`, `reversed` |
| Mapping | `__getitem__`, `__len__`, `__iter__` | `dict`-like access, `in`, `keys/values/items` |
| Hashable | `__hash__` + `__eq__` | Use as `dict` key or `set` member |
| Callable | `__call__` | Function-call syntax `obj()` |
| Context manager | `__enter__` + `__exit__` | `with` statement |

### When to Use `isinstance` Anyway

Duck typing does not mean you should never use `isinstance`. There are legitimate cases:

- **Handling `slice` objects in `__getitem__`**: You must distinguish slices from integers to return the right type.
- **Checking against ABCs**: `isinstance(obj, collections.abc.Mapping)` tests behavior, not class identity, because ABCs use `__subclasshook__`.

The rule of thumb: use `isinstance` to dispatch on *structural* categories (slice vs. int, mapping vs. sequence), not to gate-check specific classes.

## Gotchas

- **Partial protocols can surprise**: If you implement `__getitem__` without `__len__`, `len()` will fail, but `for` loops will work. This inconsistency can confuse users of your class.
- **`zip` stops silently**: This is a protocol-adjacent pitfall. If two sequences have different lengths, `zip` stops at the shorter one without warning. Use `zip(a, b, strict=True)` (Python 3.10+) when lengths must match.
- **Dynamic and static protocols can disagree**: A class might satisfy a dynamic protocol at runtime but fail a static protocol check if it does not implement every declared method.

## See Also

- [[vector-multidimensional-sequence]] -- The class that motivates this discussion
- [[sliceable-sequence-getitem]] -- Implementing the sequence protocol with proper slice handling
- [[dynamic-protocols-and-duck-typing]] -- Chapter 13's deeper treatment of protocols
- [[sequence-protocol-french-deck]] -- The Chapter 1 example that first demonstrated duck typing
