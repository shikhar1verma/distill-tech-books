---
title: "Augmented Assignment Operators: __iadd__, __imul__, etc."
book: "Fluent Python"
chapter: 16
tags: [python, operator-overloading, augmented-assignment, __iadd__, mutable, immutable]
related:
  - "[[overloading-add-and-radd]]"
  - "[[operator-overloading-rules]]"
  - "[[identity-equality-aliases]]"
---

# Augmented Assignment Operators: `__iadd__`, `__imul__`, etc.

> **One-sentence summary.** Without `__iadd__`, `a += b` desugars to `a = a.__add__(b)` (creating a new object, appropriate for immutables); mutable types should implement `__iadd__` to modify `self` in-place and return `self`; and `__iadd__` can be more liberal than `__add__` in the types it accepts.

## How It Works

Augmented assignment operators like `+=`, `*=`, `@=`, and `-=` have a dual nature in Python. Their behavior depends on whether the left operand defines an in-place special method.

### Without `__iadd__` (immutable types)

When a class does not define `__iadd__`, Python treats `a += b` exactly as `a = a + b`. This means:

1. Call `a.__add__(b)` to create a new object.
2. Rebind the name `a` to the new object.
3. The original object is untouched (and may be garbage collected if no other references exist).

This is the correct behavior for immutable types. If your class has `__add__`, it automatically supports `+=` with no extra code.

```python
v1 = Vector([1, 2, 3])
original_id = id(v1)
v1 += Vector([4, 5, 6])  # desugars to: v1 = v1 + Vector([4, 5, 6])
assert id(v1) != original_id  # a new object was created
```

### With `__iadd__` (mutable types)

When a class defines `__iadd__`, Python calls `a.__iadd__(b)` instead. The method should:

1. Modify `self` in-place.
2. **Return `self`.**

The return value matters because Python rebinds the name: `a = a.__iadd__(b)`. If `__iadd__` does not return `self`, the variable `a` gets rebound to whatever was returned (often `None` if you forget the `return self`).

```python
class AddableBingoCage(BingoCage):
    def __iadd__(self, other):
        if isinstance(other, AddableBingoCage):
            other_iterable = other.inspect()
        else:
            try:
                other_iterable = iter(other)
            except TypeError:
                raise TypeError(
                    "right operand in += must be "
                    "'AddableBingoCage' or an iterable"
                )
        self._items.extend(other_iterable)
        return self  # critical: must return self
```

## The `+` vs. `+=` Asymmetry

A key design insight: **`+=` can be more liberal than `+`** in the types it accepts for the right operand.

The `+` operator creates a new object, so the type of the result might be ambiguous if the operands are different types. It is common to restrict `+` to operands of the same type.

The `+=` operator modifies the left operand in-place. The type of the result is never ambiguous -- it is always the type of the left operand. So `+=` can safely accept any compatible input.

Python's own `list` follows this pattern:

```python
my_list = [1, 2, 3]

# + is strict: only list + list
my_list + (4, 5)      # TypeError!
my_list + range(4, 6) # TypeError!

# += is liberal: list += any iterable
my_list += (4, 5)      # OK -- works like list.extend()
my_list += range(6, 9) # OK
my_list += {10, 11}    # OK
```

The `list.__iadd__` method works exactly like `list.extend()` -- it accepts any iterable.

### The `AddableBingoCage` example

The book demonstrates this pattern with a mutable `BingoCage` subclass:

| Operation | Accepted types | Behavior |
|-----------|---------------|----------|
| `cage + other` | Only `AddableBingoCage` (via `Tombola` ABC) | Returns new instance |
| `cage += other` | Any `AddableBingoCage` or any iterable | Modifies `cage` in-place |

The `__add__` method checks `isinstance(other, Tombola)` and returns `NotImplemented` otherwise. The `__iadd__` method first checks for `Tombola`, then falls back to trying `iter(other)` for any iterable.

## No `__radd__` Needed for Strict `__add__`

If your `__add__` only accepts operands of the same type, there is no point implementing `__radd__`. Consider: `__radd__` is only called when the left operand's `__add__` fails. If `a` is not an `AddableBingoCage`, we cannot produce an `AddableBingoCage` from `a + cage` anyway. Letting Python raise `TypeError` is the correct behavior.

This is a general rule: if a forward infix operator method only works with operands of the same type as `self`, the corresponding reverse method is useless.

## Implementation Rules

1. **Never implement `__iadd__` for immutable types.** The default behavior (creating a new object via `__add__` and rebinding) is exactly right.

2. **Always return `self`** from in-place operator methods. Forgetting `return self` is a subtle bug -- `a += b` will set `a` to `None`.

3. **`+=` error messages should guide the user.** Since `__iadd__` may accept broader types than `__add__`, a custom error message explaining what is accepted is more helpful than a generic `TypeError`.

4. **In-place operators should not return `NotImplemented`.** Unlike `__add__`, which returns `NotImplemented` to trigger the reverse method, `__iadd__` should either succeed or raise a clear exception. The dispatch protocol for augmented assignment does fall back to `__add__` + rebinding if `__iadd__` returns `NotImplemented`, but this creates confusing behavior for mutable types.

## The Full Method Name Table

| Operator | Forward | Reverse | In-place |
|----------|---------|---------|----------|
| `+=` | `__add__` | `__radd__` | `__iadd__` |
| `-=` | `__sub__` | `__rsub__` | `__isub__` |
| `*=` | `__mul__` | `__rmul__` | `__imul__` |
| `@=` | `__matmul__` | `__rmatmul__` | `__imatmul__` |
| `/=` | `__truediv__` | `__rtruediv__` | `__itruediv__` |
| `//=` | `__floordiv__` | `__rfloordiv__` | `__ifloordiv__` |
| `**=` | `__pow__` | `__rpow__` | `__ipow__` |

## Connection to Other Concepts

Augmented assignment builds on the `__add__`/`__radd__` dispatch protocol (see [[overloading-add-and-radd]]). The distinction between in-place and copy semantics connects to Python's fundamental model of variables as labels on objects (see [[identity-equality-aliases]]). The `+` vs. `+=` asymmetry is a practical application of the operator overloading rules in [[operator-overloading-rules]].
