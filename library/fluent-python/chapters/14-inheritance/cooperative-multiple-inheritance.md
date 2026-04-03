---
title: "Cooperative Multiple Inheritance"
book: "Fluent Python"
chapter: 14
tags: [python, oop, multiple-inheritance, super, cooperative]
related:
  - "[[super-function]]"
  - "[[multiple-inheritance-mro]]"
  - "[[mixin-classes]]"
---

# Cooperative Multiple Inheritance

> **One-sentence summary.** When every method in a class hierarchy calls `super()`, the entire MRO chain is traversed cooperatively; if any method breaks the chain by omitting `super()`, all downstream classes are silently skipped.

## How It Works

A method that calls `super()` is called a **cooperative method**. When all methods with the same name across a multiple inheritance hierarchy are cooperative, they form a **cooperative chain**: each method does its work and then delegates to the next class in the MRO. The chain terminates at the root class (the one that does not call `super()` for that method, typically because it provides the base implementation).

The key insight is that `super()` is **dynamic** — it does not resolve at class-definition time but at call time, based on the MRO of the actual instance's class.

```python
class Root:
    def ping(self):
        print("  ping() in Root")  # root: no super() call

class A(Root):
    def ping(self):
        print("  ping() in A")
        super().ping()             # cooperative

class B(Root):
    def ping(self):
        print("  ping() in B")
        super().ping()             # cooperative

class Leaf(A, B):
    def ping(self):
        print("  ping() in Leaf")
        super().ping()             # cooperative

Leaf().ping()
# ping() in Leaf → A → B → Root  (full chain!)
```

### What happens when cooperation breaks

If `B.ping()` omits the `super().ping()` call, the chain stops at `B` — `Root.ping()` is never reached. No error is raised; the method simply does not execute for the remaining classes.

### Dynamic MRO means dynamic super()

A class defined in isolation might seem to have `object` as its only superclass. But when that class is mixed into a hierarchy, `super()` can reach classes that did not exist when the class was written:

```python
class U:
    def ping(self):
        print("  ping() in U")
        super().ping()  # At definition time, super() would reach object

class LeafUA(U, A):
    def ping(self):
        print("  ping() in LeafUA")
        super().ping()

# LeafUA MRO: LeafUA -> U -> A -> Root -> object
# U.ping()'s super().ping() now reaches A.ping()!
LeafUA().ping()
```

## In Practice

**Compatible signatures are required.** Because you don't know which class will be next in the MRO at any given call, cooperative methods must have compatible parameter signatures. The common pattern for `__init__` is to accept `**kwargs` and forward them:

```python
class MyMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # mixin-specific setup
```

**Every non-root method should call super().** This is the fundamental rule. Even if your current hierarchy works without it, a future subclass using multiple inheritance could silently lose method calls.

**Root classes define the termination point.** The root of a cooperative chain typically does not call `super()` for domain-specific methods. For `__init__`, `object.__init__()` serves as the natural root.

## Common Pitfalls

- **Silent chain breakage**: A single missing `super()` call stops the chain. There is no warning — downstream classes simply don't participate.
- **Incompatible signatures**: If `A.process(self, x)` and `B.process(self, x, y)` are in the same chain, the call will fail with a TypeError at the link where signatures don't match.
- **Forgetting that MRO is per-class, not per-method**: The *same* MRO applies to all methods. You can't have `ping` follow one order and `pong` follow another on the same instance.
- **Assuming a fixed super() target**: `super()` in class `U` might reach `object` when `U` is used alone, but reach `A` when `U` is part of `LeafUA`. Design accordingly.

## See Also

- [[super-function]] — the mechanism that walks the MRO
- [[multiple-inheritance-mro]] — how C3 linearization determines the chain order
- [[mixin-classes]] — the most common pattern that relies on cooperative dispatch
