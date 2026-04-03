---
title: "Python's Rules and Best Practices for Operator Overloading"
book: "Fluent Python"
chapter: 16
tags: [python, operator-overloading, best-practices, NotImplemented, duck-typing, goose-typing]
related:
  - "[[unary-operators]]"
  - "[[overloading-add-and-radd]]"
  - "[[overloading-mul-and-matmul]]"
  - "[[rich-comparison-operators]]"
  - "[[augmented-assignment-operators]]"
  - "[[special-dunder-methods]]"
---

# Python's Rules and Best Practices for Operator Overloading

> **One-sentence summary.** Python's operator overloading constraints prevent abuse (cannot redefine ops for built-ins, cannot create new operators, `is`/`and`/`or`/`not` cannot be overloaded) while best practices dictate returning new objects from operators, returning `NotImplemented` for unsupported types, using duck typing or goose typing for type checks, and never mutating operands in non-augmented operators.

## The Constraints

Python imposes three fundamental restrictions on operator overloading that prevent the worst abuses seen in languages like C++:

### 1. Cannot redefine operators for built-in types

You cannot change what `int.__add__` does or make `str.__mul__` behave differently. Built-in type operators are fixed. This guarantees that core Python semantics remain predictable.

### 2. Cannot create new operators

Unlike Haskell or Scala, Python does not allow you to define custom operator symbols. You can only overload existing operators. The full set is defined by the language grammar.

### 3. Certain operators cannot be overloaded

- `is` -- always tests object identity
- `and` -- always short-circuits on truthiness
- `or` -- always short-circuits on truthiness
- `not` -- always returns a `bool` based on truthiness

However, the **bitwise** counterparts `&`, `|`, `~` can be overloaded. This distinction is important: SQLAlchemy and pandas overload bitwise operators to build query expressions and boolean masks respectively.

## The Dispatch Protocol

When Python evaluates an infix operator expression `a + b`, it follows a well-defined protocol:

1. Call `a.__add__(b)`. If the result is not `NotImplemented`, return it.
2. Call `b.__radd__(a)`. If the result is not `NotImplemented`, return it.
3. Raise `TypeError`.

There is one exception to this order: if `b` is an instance of a **subclass** of `a`'s class, Python tries `b.__radd__(a)` first. This ensures that subclass implementations take precedence, which is essential for correct polymorphism.

### Rich comparisons use mirror methods

Comparison operators do not have `__r*__` methods. Instead:
- The reverse of `__gt__` is `__lt__` (with swapped operands)
- The reverse of `__ge__` is `__le__` (with swapped operands)
- `__eq__` is its own reverse (called on the other operand)

The `==` operator has a unique fallback: identity comparison. The ordering operators (`<`, `>`, `<=`, `>=`) raise `TypeError` if neither side can handle the comparison.

## Best Practices

### 1. Return `NotImplemented`, do not raise `TypeError`

This is the single most important rule. `NotImplemented` is a signal to the interpreter meaning "I cannot handle this operand type, please try the other side." Raising `TypeError` immediately terminates the dispatch -- the other operand never gets a chance.

```python
# WRONG: cuts off the dispatch protocol
def __add__(self, other):
    if not isinstance(other, Vector):
        raise TypeError(f"unsupported type: {type(other)}")
    ...

# RIGHT: gives the other operand a chance
def __add__(self, other):
    if not isinstance(other, Vector):
        return NotImplemented
    ...
```

### 2. Always return new objects from non-augmented operators

Expressions like `a + b`, `a * b`, and `-a` must never modify `a` or `b`. Users expect these expressions to produce new objects. Only augmented assignment operators (`__iadd__`, `__imul__`, etc.) on mutable types should modify `self`.

### 3. Use duck typing or goose typing for type checks

Avoid rigid isinstance checks against concrete types. Two strategies are used in Chapter 16:

**Duck typing** (used in `__add__` and `__mul__`): Try the operation, catch `TypeError`, return `NotImplemented` on failure. This is maximally flexible -- any type that supports the required protocol works.

```python
def __add__(self, other):
    try:
        pairs = itertools.zip_longest(self, other, fillvalue=0.0)
        return Vector(a + b for a, b in pairs)
    except TypeError:
        return NotImplemented
```

**Goose typing** (used in `__matmul__`): Check isinstance against ABCs like `abc.Sized` and `abc.Iterable`. This provides structural guarantees without coupling to concrete types. Any object that implements `__len__` and `__iter__` qualifies, even without explicit ABC registration.

```python
def __matmul__(self, other):
    if isinstance(other, abc.Sized) and isinstance(other, abc.Iterable):
        ...
    return NotImplemented
```

**When to use which?** Duck typing works best when a simple operation (like `float(scalar)` or iterating) naturally validates the input. Goose typing works best when you need structural guarantees before starting a complex computation.

### 4. Augmented assignment: `+` strict, `+=` liberal

For the `+` operator, restrict operands to the same type (or compatible types) because the result type would be ambiguous otherwise. For `+=`, accept any compatible input because the result type is always the type of the left operand.

### 5. Skip `__ne__` -- inherit it from `object`

The default `__ne__` negates `__eq__`. It handles `NotImplemented` correctly. Implementing `__ne__` yourself is almost never necessary and risks introducing inconsistencies.

### 6. Use `@functools.total_ordering` for comparisons

If you need all six comparison operators, define `__eq__` and one ordering method (like `__lt__`), then decorate with `@total_ordering` to get the rest.

## The Complete Operator Table

### Arithmetic operators (forward / reverse / in-place)

| Operator | Forward | Reverse | In-place |
|----------|---------|---------|----------|
| `+` | `__add__` | `__radd__` | `__iadd__` |
| `-` | `__sub__` | `__rsub__` | `__isub__` |
| `*` | `__mul__` | `__rmul__` | `__imul__` |
| `/` | `__truediv__` | `__rtruediv__` | `__itruediv__` |
| `//` | `__floordiv__` | `__rfloordiv__` | `__ifloordiv__` |
| `%` | `__mod__` | `__rmod__` | `__imod__` |
| `**` | `__pow__` | `__rpow__` | `__ipow__` |
| `@` | `__matmul__` | `__rmatmul__` | `__imatmul__` |

### Bitwise operators

| Operator | Forward | Reverse | In-place |
|----------|---------|---------|----------|
| `&` | `__and__` | `__rand__` | `__iand__` |
| `\|` | `__or__` | `__ror__` | `__ior__` |
| `^` | `__xor__` | `__rxor__` | `__ixor__` |
| `<<` | `__lshift__` | `__rlshift__` | `__ilshift__` |
| `>>` | `__rshift__` | `__rrshift__` | `__irshift__` |

### Unary operators

| Operator | Method |
|----------|--------|
| `-x` | `__neg__` |
| `+x` | `__pos__` |
| `~x` | `__invert__` |
| `abs(x)` | `__abs__` |

## Real-World Examples Beyond Mathematics

Operator overloading is not limited to numeric types:

- **`pathlib.Path`** overloads `/` to build filesystem paths: `Path('/etc') / 'init.d' / 'reboot'`
- **Scapy** overloads `/` to stack network protocol layers
- **pandas** overloads `~`, `&`, `|` for boolean mask operations
- **SQLAlchemy** overloads `==`, `!=`, `<`, `>` to build SQL WHERE clauses

These examples show that operator overloading, when used thoughtfully, creates APIs that are both concise and readable.

## Connection to Other Concepts

This article is the theoretical foundation for all operator overloading in Chapter 16. Each specific operator type is covered in detail: [[unary-operators]] for `-`, `+`, `~`, `abs()`; [[overloading-add-and-radd]] for the `+` dispatch protocol; [[overloading-mul-and-matmul]] for `*` and `@`; [[rich-comparison-operators]] for `==`, `!=`, `<`, `>`, etc.; and [[augmented-assignment-operators]] for `+=`, `*=`, etc. The special methods covered here are a subset of the Python Data Model described in Chapter 1 (see [[special-dunder-methods]]).
