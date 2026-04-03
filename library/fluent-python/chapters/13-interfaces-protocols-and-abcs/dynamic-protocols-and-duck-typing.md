---
title: "Dynamic Protocols and Duck Typing"
chapter: 13
slug: dynamic-protocols-and-duck-typing
type: mixed
depends_on:
  - typing-map-four-approaches
tags:
  - duck-typing
  - protocols
  - monkey-patching
  - EAFP
  - sequences
---

# Dynamic Protocols and Duck Typing

Dynamic protocols are the informal interfaces Python has always had. They are implicit, defined by convention, and documented in the Data Model chapter of the Python Language Reference. The interpreter actively cooperates with objects that provide even a **partial** implementation.

## Python Digs Sequences

The `Sequence` protocol formally requires `__getitem__` and `__len__`, but implementing just `__getitem__` is enough for the interpreter to provide:

- **Indexing:** `obj[i]`
- **Iteration:** `for x in obj` (fallback to calling `__getitem__` with 0, 1, 2, ...)
- **Containment:** `x in obj` (sequential scan via `__getitem__`)

```python
class Vowels:
    def __getitem__(self, i):
        return 'AEIOU'[i]

v = Vowels()
print(v[0])          # 'A'
print('E' in v)      # True
print([c for c in v])  # ['A', 'E', 'I', 'O', 'U']
```

This extreme cooperativeness is why protocols are called "informal interfaces."

## Two Kinds of Protocols

| Feature | Dynamic Protocol | Static Protocol |
|---|---|---|
| Definition | By convention / docs | Explicit `typing.Protocol` subclass |
| Partial implementation | Often useful | Must implement all methods |
| Type checker support | No | Yes |
| Class declaration | Never needed | Never needed |

Both share the essential characteristic: a class **never needs to declare** support for a protocol by name.

## Monkey Patching

Monkey patching adds or replaces methods on a class at runtime. This can make a class implement a protocol *after* it was defined.

```python
# FrenchDeck lacks __setitem__, so random.shuffle fails.
# Fix at runtime:
def set_card(deck, position, card):
    deck._cards[position] = card

FrenchDeck.__setitem__ = set_card
# Now random.shuffle(deck) works!
```

**Caveats:** Monkey patching creates tight coupling with internal implementation details. Python prevents monkey patching built-in types (`str`, `list`, etc.).

## Defensive Programming and Fail Fast

Duck typing stays safe through disciplined defensive coding:

### Convert eagerly
```python
def __init__(self, iterable):
    self._balls = list(iterable)  # TypeError if not iterable
```
Building a `list` immediately catches bad arguments and makes a defensive copy.

### EAFP pattern
```python
try:
    field_names = field_names.replace(',', ' ').split()
except AttributeError:
    pass  # Not a string -- assume iterable of strings
field_names = tuple(field_names)
```
Try the operation first; handle the exception if the object doesn't support it.

### Use `iter()` and `len()` as guards
- `iter(x)` -- raises `TypeError` immediately if `x` is not iterable
- `len(x)` -- rejects iterators (which don't have length), cheap check

## Key Takeaways

1. The interpreter goes to great lengths to make partial protocol implementations work.
2. Monkey patching can add protocol methods at runtime, but use with caution.
3. Defensive programming (fail fast, EAFP) keeps duck typing safe and debuggable.
4. Duck typing cannot be fully captured by static type hints -- `Any` inference can blind type checkers.

## See Also

- [[typing-map-four-approaches]] -- where duck typing fits in the typing map
- [[goose-typing-and-abcs]] -- a more explicit runtime alternative
- [[static-protocols-typing-protocol]] -- the static counterpart
