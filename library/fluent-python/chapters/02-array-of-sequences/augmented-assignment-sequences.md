---
title: "Augmented Assignment with Sequences"
book: "Fluent Python"
chapter: 2
tags: [augmented-assignment, iadd, imul, mutability, sequences, puzzler]
related:
  - "[[tuples-as-records-and-immutable-lists]]"
  - "[[slicing]]"
  - "[[slicing]]"
---

## Summary

The `+=` and `*=` operators behave differently depending on mutability. Mutable sequences (like `list`) implement `__iadd__`/`__imul__` for in-place modification. Immutable sequences (like `tuple`) fall back to `__add__`/`__mul__`, creating new objects. This distinction leads to subtle identity changes and the famous tuple `+=` puzzler.

## How It Works

### Mutable Sequences: In-Place Modification

When `a` implements `__iadd__`, `a += b` modifies `a` in place (similar to `a.extend(b)`). The object identity does not change:

```python
l = [1, 2, 3]
original_id = id(l)
l *= 2
assert id(l) == original_id  # same object
# l is now [1, 2, 3, 1, 2, 3]
```

### Immutable Sequences: New Object

For tuples and strings, `+=` creates a new object and rebinds the variable:

```python
t = (1, 2, 3)
original_id = id(t)
t *= 2
assert id(t) != original_id  # different object!
# t is now (1, 2, 3, 1, 2, 3)
```

Repeated concatenation of immutable sequences is O(n^2) because each step copies the entire existing sequence. (CPython optimizes `str +=` as a special case.)

### The `+=` Puzzler

The most surprising behavior occurs when `+=` is applied to a mutable item inside an immutable container:

```python
t = (1, 2, [30, 40])
try:
    t[2] += [50, 60]
except TypeError:
    pass

# Both things happened:
# 1. The list t[2] was extended: [30, 40, 50, 60]
# 2. TypeError was raised: 'tuple' object does not support item assignment
print(t)  # (1, 2, [30, 40, 50, 60])
```

**Why?** Looking at the bytecode for `s[a] += b`:
1. `BINARY_SUBSCR` -- get `s[a]` (the list) onto the stack.
2. `INPLACE_ADD` -- perform `list.__iadd__([50, 60])` on the list. This **succeeds**.
3. `STORE_SUBSCR` -- try `s[a] = result`. This **fails** because `s` is a tuple.

The operation is not atomic: step 2 mutates the list before step 3 fails.

## In Practice

- For **mutable sequences**, `+=` and `*=` are efficient in-place operations.
- For **immutable sequences**, avoid `+=` in tight loops (use `str.join()` for strings, or build a list and convert).
- Never rely on `+=` being atomic -- it is a multi-step operation at the bytecode level.

## Common Pitfalls

1. **Mutable items in tuples.** The `+=` puzzler is a consequence of mixing mutable and immutable containers. Avoid putting lists inside tuples.
2. **Assuming identity is preserved.** `t += (4,)` where `t` is a tuple creates a new tuple and rebinds `t`. If another variable references the old tuple, it still points to the old one.
3. **Performance trap with immutable `+=`.** `s += 'x'` in a loop on a string is O(n^2) in the worst case (CPython optimizes it, but PyPy and other implementations may not).
4. **`*` with mutable items.** `[[]] * 3` creates three references to the same list. Use a listcomp instead: `[[] for _ in range(3)]`.

## See Also

- [[tuples-as-records-and-immutable-lists]] -- why tuples with mutable items are problematic
- [[slicing]] -- another way to modify sequences in place
- Chapter 16 covers `__iadd__` and `__imul__` implementation in detail
