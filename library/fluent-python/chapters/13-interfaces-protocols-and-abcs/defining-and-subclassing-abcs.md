---
title: "Defining and Subclassing ABCs"
chapter: 13
slug: defining-and-subclassing-abcs
type: code-heavy
depends_on:
  - goose-typing-and-abcs
tags:
  - ABCs
  - abstractmethod
  - abc-ABC
  - Tombola
  - concrete-methods
---

# Defining and Subclassing ABCs

This article walks through designing a custom ABC (Tombola) and implementing concrete subclasses, illustrating how abstract and concrete methods interact.

## Defining an ABC: Tombola

```python
import abc

class Tombola(abc.ABC):
    @abc.abstractmethod
    def load(self, iterable):
        """Add items from an iterable."""

    @abc.abstractmethod
    def pick(self):
        """Remove item at random, returning it.
        Should raise LookupError when empty.
        """

    def loaded(self):
        """Return True if there is at least one item."""
        return bool(self.inspect())

    def inspect(self):
        """Return a sorted tuple of current items."""
        items = []
        while True:
            try:
                items.append(self.pick())
            except LookupError:
                break
        self.load(items)
        return tuple(items)
```

### Key design points

1. **Subclass `abc.ABC`** to declare an abstract base class.
2. **`@abc.abstractmethod`** marks methods that subclasses must implement. The decorator should always be the **innermost** decorator when stacked.
3. **Concrete methods** (`loaded`, `inspect`) rely only on the ABC's own interface -- they call `pick()` and `load()` without knowing the internal storage.
4. **LookupError** is specified in the docstring as the exception `pick()` should raise when empty. Python cannot enforce this mechanically -- it's a semantic contract.
5. Abstract methods **can** have implementations. Subclasses can call `super().pick()` to extend rather than replace.

### Enforcement is at instantiation, not import

```python
class Fake(Tombola):
    def pick(self): return 13
    # Missing: load()

Fake  # Class object is created -- no error
f = Fake()  # TypeError: Can't instantiate abstract class Fake
            #           with abstract method load
```

## ABC Syntax Details

```python
class MyABC(abc.ABC):
    @classmethod
    @abc.abstractmethod         # Must be innermost
    def an_abstract_classmethod(cls, ...):
        pass

    @staticmethod
    @abc.abstractmethod         # Must be innermost
    def an_abstract_staticmethod(...):
        pass
```

The deprecated `@abstractclassmethod`, `@abstractstaticmethod`, and `@abstractproperty` decorators from Python < 3.3 are replaced by stacking decorators above `@abstractmethod`.

## Concrete Subclass: BingoCage

```python
class BingoCage(Tombola):
    def __init__(self, items):
        self._randomizer = random.SystemRandom()
        self._items = []
        self.load(items)

    def load(self, items):
        self._items.extend(items)
        self._randomizer.shuffle(self._items)

    def pick(self):
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError('pick from empty BingoCage')
```

BingoCage inherits the (expensive) `loaded` and `inspect` from Tombola. They work correctly but could be overridden for performance.

## Concrete Subclass: LottoBlower

```python
class LottoBlower(Tombola):
    def __init__(self, iterable):
        self._balls = list(iterable)  # Defensive copy

    def load(self, iterable):
        self._balls.extend(iterable)

    def pick(self):
        try:
            position = random.randrange(len(self._balls))
        except ValueError:
            raise LookupError('pick from empty LottoBlower')
        return self._balls.pop(position)

    def loaded(self):       # Override: O(1) instead of O(n)
        return bool(self._balls)

    def inspect(self):      # Override: O(n) copy instead of O(n^2)
        return tuple(self._balls)
```

### Design patterns

- **Defensive initialization:** `list(iterable)` copies the input and fails fast if not iterable.
- **Override concrete methods** when you can exploit knowledge of internal data structures for better performance.
- **Exception translation:** catch `ValueError`/`IndexError` and raise `LookupError` to satisfy the ABC contract.

## Inherited Mixin Methods

When subclassing `collections.abc.MutableSequence`, implementing 5 abstract methods gives you 11 concrete methods for free:

| From `Sequence` | From `MutableSequence` |
|---|---|
| `__contains__` | `append` |
| `__iter__` | `reverse` |
| `__reversed__` | `extend` |
| `index` | `pop` |
| `count` | `remove` |
| | `__iadd__` (`+=`) |

## See Also

- [[goose-typing-and-abcs]] -- when and why to use ABCs
- [[virtual-subclasses-and-register]] -- an alternative to subclassing
- [[static-protocols-typing-protocol]] -- the static alternative to ABCs
