---
title: "The Sequence Protocol: FrenchDeck"
book: "Fluent Python"
chapter: 1
tags: [python, data-model, sequence, protocol, getitem, len, namedtuple]
related:
  - "[[special-dunder-methods]]"
  - "[[collection-api-abcs]]"
  - "[[numeric-type-emulation]]"
---

## Summary

The `FrenchDeck` class from Chapter 1 demonstrates that implementing just `__getitem__` and `__len__` is enough to make a custom class behave like a full Python sequence. With these two methods, you automatically get indexing, slicing, iteration, membership testing (`in`), `reversed()`, `sorted()`, and compatibility with standard library functions like `random.choice`.

## How It Works

The FrenchDeck uses `collections.namedtuple` to define a lightweight `Card` type, then stores 52 cards in an internal list. The two special methods delegate to the internal list:

```python
import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

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

Here is what these two methods unlock:

**Indexing and slicing** -- Because `__getitem__` delegates to a list, anything you can do with list indexing works on the deck:

```python
deck = FrenchDeck()
deck[0]        # Card(rank='2', suit='spades')
deck[-1]       # Card(rank='A', suit='hearts')
deck[:3]       # first three cards
deck[12::13]   # all four aces
```

**Iteration** -- Python's `for` loop tries `__iter__` first. When that is not found, it falls back to calling `__getitem__` with successive integer indices (0, 1, 2, ...) until `IndexError` is raised. This is the legacy **sequence protocol**.

```python
for card in deck:      # works via __getitem__ fallback
    print(card)

for card in reversed(deck):  # reversed() also uses __getitem__ + __len__
    print(card)
```

**Membership testing** -- Without `__contains__`, the `in` operator performs a linear scan using iteration:

```python
Card('Q', 'hearts') in deck   # True
Card('7', 'beasts') in deck   # False
```

**Standard library integration** -- Because FrenchDeck is a sequence, functions like `random.choice`, `sorted`, `min`, `max` all work:

```python
from random import choice
choice(deck)   # picks a random card

sorted(deck, key=some_ranking_function)  # sorted copy
```

### The Composition Pattern

FrenchDeck does not inherit from `list` or any ABC. Instead, it uses **composition**: it stores a list internally and delegates `__len__` and `__getitem__` to it. This is a lightweight, flexible pattern -- the class can control what it exposes without being locked into a superclass hierarchy.

### Why Not `__setitem__`?

As implemented, FrenchDeck is **immutable** -- you cannot assign to positions or shuffle it in place. Adding a one-line `__setitem__` method (covered in Chapter 13) would make it mutable:

```python
def __setitem__(self, position, value):
    self._cards[position] = value
```

## In Practice

The sequence protocol pattern is extremely common in real-world Python:

- **ORM query results** -- Database libraries like SQLAlchemy and Django return query results as sequence-like objects with `__getitem__` and `__len__`.
- **Lazy sequences** -- You can implement `__getitem__` to compute values on-the-fly rather than storing them all in memory.
- **Custom containers** -- Any class wrapping a list, tuple, or array benefits from this pattern.

The `namedtuple` used for `Card` is also widely used for lightweight data classes. In modern Python (3.7+), `dataclasses.dataclass` is a more feature-rich alternative, but `namedtuple` remains useful for immutable, tuple-compatible records.

## Common Pitfalls

1. **Assuming `__getitem__` requires `__iter__`.** It does not. Python's `for` loop and `in` operator have a fallback that uses `__getitem__` with integer indices. However, defining `__iter__` is preferred for new code because it is more explicit.

2. **Forgetting that ABC isinstance checks are stricter.** `isinstance(deck, Iterable)` returns `False` for FrenchDeck (no `__iter__`), even though `for card in deck` works fine. The ABC checks look for the explicit method, not the `__getitem__` fallback.

3. **Mutability confusion.** Without `__setitem__`, `random.shuffle(deck)` will raise `TypeError`. If you need in-place mutation, you must implement `__setitem__` (and possibly `__delitem__`).

4. **Using inheritance when composition suffices.** Inheriting from `list` exposes methods like `append`, `pop`, and `sort` that you may not want on your custom class. Composition gives you precise control.

## See Also

- [[special-dunder-methods]] -- The broader framework that makes this pattern work
- [[collection-api-abcs]] -- Formal definitions of Sequence, Iterable, Sized, Container
- [[numeric-type-emulation]] -- Another example of using special methods (for operators instead of sequences)
