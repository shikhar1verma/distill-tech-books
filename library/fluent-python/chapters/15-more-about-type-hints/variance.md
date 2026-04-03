---
title: "Variance: Covariant, Contravariant, and Invariant"
book: "Fluent Python"
chapter: 15
tags: [python, type-hints, variance, covariant, contravariant, invariant, generics]
related:
  - "[[generic-classes]]"
  - "[[generic-static-protocols]]"
---

# Variance: Covariant, Contravariant, and Invariant

> **One-sentence summary.** Variance describes how subtype relationships between type parameters affect subtype relationships between parameterized generic types -- invariant means exact match only, covariant follows the subtype direction, and contravariant reverses it.

## How It Works

Consider three beverage types forming a hierarchy: `Beverage` (base) > `Juice` > `OrangeJuice`. A school cafeteria requires juice dispensers. The question is: which parameterized dispenser types are acceptable?

### Invariant (default)

With a plain `TypeVar("T")`, `BeverageDispenser[Juice]` is the ONLY acceptable type. Neither `BeverageDispenser[Beverage]` (too general) nor `BeverageDispenser[OrangeJuice]` (too specific) is compatible. Python's mutable collections (`list`, `set`, `dict`) are invariant.

```python
from typing import TypeVar, Generic
T = TypeVar("T")  # invariant by default

class BeverageDispenser(Generic[T]):
    def __init__(self, beverage: T) -> None:
        self.beverage = beverage
    def dispense(self) -> T:
        return self.beverage
```

### Covariant

With `TypeVar("T_co", covariant=True)`, `BeverageDispenser[Juice]` AND `BeverageDispenser[OrangeJuice]` are both acceptable. The subtype relationship flows in the **same direction** as the type parameters: since `OrangeJuice <: Juice`, then `Dispenser[OrangeJuice] <: Dispenser[Juice]`.

Immutable containers and iterators are naturally covariant because they only produce output. `frozenset`, `tuple`, and `Iterator` are covariant in the standard library.

### Contravariant

Now consider trash cans. A `TrashCan[Biodegradable]` is required. With `TypeVar("T_contra", contravariant=True)`, `TrashCan[Biodegradable]` AND `TrashCan[Refuse]` (the more general type) are acceptable. The subtype relationship is **reversed**: since `Refuse :> Biodegradable`, then `TrashCan[Refuse] <: TrashCan[Biodegradable]`.

Contravariant types are "sinks" -- they accept input. `Callable` is contravariant in its parameter types for this reason: a function accepting `Animal` can be used wherever a function accepting `Cat` is expected.

```python
T_contra = TypeVar("T_contra", contravariant=True)

class TrashCan(Generic[T_contra]):
    def put(self, refuse: T_contra) -> None: ...
```

## In Practice

The rules of thumb for choosing variance:

1. **Output only** (return types, yielded values) -- use **covariant** (`T_co`)
2. **Input only** (method parameters after construction) -- use **contravariant** (`T_contra`)
3. **Both input and output** (mutable collections) -- must be **invariant** (`T`)
4. **When in doubt** -- use invariant; it is always safe

`Callable[[ParamType], ReturnType]` is the canonical example of mixed variance: `ParamType` is contravariant (input), `ReturnType` is covariant (output).

The `:>` notation helps visualize this:

```
           float :> int
frozenset[float] :> frozenset[int]     # covariant -- same direction

          Refuse :> Biodegradable
TrashCan[Refuse] <: TrashCan[Biodegradable]  # contravariant -- reversed
```

## Common Pitfalls

- **Making mutable containers covariant**: If a `list[int]` were covariant and assignable to `list[float]`, you could append a `float` to what is actually a `list[int]` at runtime. This is why mutable collections must be invariant.
- **Confusing the TypeVar with the class**: PEP 484 notes that variance is a property of the generic class, not the TypeVar itself. But Python's syntax forces you to declare it on the TypeVar. The `_co` and `_contra` naming conventions help communicate intent.
- **Ignoring variance for library APIs**: If you design a generic container for others to use, think about whether consumers need covariance (read-only access) or invariance (read-write). Getting this wrong limits the usability of your API.

## See Also

- [[generic-classes]] -- the foundation for understanding variance
- [[generic-static-protocols]] -- protocols are typically covariant because they define output interfaces
