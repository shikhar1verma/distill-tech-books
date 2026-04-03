---
title: "Multiple Inheritance and Method Resolution Order"
book: "Fluent Python"
chapter: 14
tags: [python, oop, multiple-inheritance, mro, c3-linearization]
related:
  - "[[super-function]]"
  - "[[cooperative-multiple-inheritance]]"
  - "[[mixin-classes]]"
---

# Multiple Inheritance and Method Resolution Order

> **One-sentence summary.** Python's MRO, computed by the C3 linearization algorithm and stored in `__mro__`, determines the deterministic order in which base classes are searched when resolving method calls through `super()`.

## How It Works

When a class has multiple base classes, a method call could match definitions in several ancestors. Python resolves this ambiguity with the **Method Resolution Order (MRO)** — a linear sequence of classes that `super()` walks through. Every class has a `__mro__` attribute holding a tuple of class references from the current class to `object`.

The MRO is computed at class creation time using the **C3 linearization** algorithm, which guarantees:
1. Subclasses appear before their parents
2. The order of base classes in the `class` statement is preserved
3. A common ancestor is deferred until all its descendants have been visited

```python
class Root:
    def ping(self):
        print(f"  ping() in Root")

class A(Root):
    def ping(self):
        print(f"  ping() in A")
        super().ping()

class B(Root):
    def ping(self):
        print(f"  ping() in B")
        super().ping()

class Leaf(A, B):
    def ping(self):
        print(f"  ping() in Leaf")
        super().ping()

# Inspect the MRO
print([c.__name__ for c in Leaf.__mro__])
# ['Leaf', 'A', 'B', 'Root', 'object']

Leaf().ping()
# ping() in Leaf
# ping() in A
# ping() in B
# ping() in Root
```

### Declaration order matters

If `Leaf` were declared as `Leaf(B, A)`, the MRO would be `[Leaf, B, A, Root, object]` — `B` before `A`. This directly affects which methods run and in what order.

### The diamond problem

The "diamond" arises when two parent classes share a common ancestor. Without C3 linearization, the common ancestor could be visited more than once or in the wrong order. C3 guarantees it appears exactly once, after all its descendants.

## In Practice

**Debugging MRO issues**: When method dispatch behaves unexpectedly in a multiple inheritance hierarchy, print the `__mro__`:

```python
print(MyClass.__mro__)
# or for readability:
print(', '.join(c.__name__ for c in MyClass.__mro__))
```

**MRO conflicts**: Python will raise a `TypeError` at class creation time if C3 linearization cannot produce a consistent ordering. This happens with certain contradictory inheritance graphs — it is intentional and protects you from ambiguous hierarchies.

**The MRO only determines search order** — whether a method actually gets called at each step depends on whether the previous method in the chain calls `super()`. The MRO defines the *potential* path; `super()` calls walk it.

## Common Pitfalls

- **Confusing MRO with breadth-first search**: The MRO may look like BFS in simple cases, but it is computed by C3 linearization, which has different guarantees.
- **Assuming the MRO is static across all subclasses**: A class `A` might appear before `B` in one subclass's MRO but after `B` in another's, depending on declaration order.
- **Ignoring `__mro__` when debugging**: Many inheritance bugs become obvious once you print the MRO.

## See Also

- [[super-function]] — how `super()` uses the MRO to delegate calls
- [[cooperative-multiple-inheritance]] — why every method must call `super()` for the full chain to work
- [[mixin-classes]] — a practical pattern that relies on correct MRO ordering
