---
title: "The Relative Immutability of Tuples"
slug: relative-immutability-of-tuples
chapter: 6
book: fluent-python
type: mixed
depends_on:
  - identity-equality-aliases
tags: [tuples, immutability, references, hashable, mutable-items]
---

# The Relative Immutability of Tuples

## The Surprise

Tuples are immutable -- but their **value** can change.

This sounds contradictory until you understand what "immutable" means for a container. A tuple holds **references** to objects. Immutability means:

- You cannot add, remove, or replace references in the tuple.
- But if a reference points to a **mutable** object, that object can still change.

```python
t1 = (1, 2, [30, 40])
t2 = (1, 2, [30, 40])

t1 == t2              # True -- equal values

t1[-1].append(99)     # Mutate the list inside t1
t1                    # (1, 2, [30, 40, 99])
t1 == t2              # False -- values diverged!
```

The tuple `t1` itself was never modified -- no items were added or removed. But the list it holds at index `[-1]` was mutated in place, changing the tuple's observable value.

## What Stays Fixed

The **identity** of every item in the tuple is fixed forever:

```python
t = (1, 2, [30, 40])
original_id = id(t[-1])

t[-1].append(99)
id(t[-1]) == original_id  # True -- same list object
```

You can mutate the list all you want, but you can never make `t[-1]` point to a different object.

## The `+=` Puzzler

This is a famous Python gotcha:

```python
t = (1, [2, 3])
t[1] += [4, 5]
# Raises TypeError... but also mutates t[1]!
# t is now (1, [2, 3, 4, 5])
```

What happens step by step:
1. `t[1]` retrieves the list `[2, 3]`.
2. `+= [4, 5]` extends the list in place to `[2, 3, 4, 5]` (mutation succeeds).
3. The result is assigned back to `t[1]` -- this fails because tuples don't support item assignment.

So you get **both** the mutation **and** the exception.

## Hashability Implications

A tuple is hashable only if **all** its items are hashable:

```python
hash((1, 2, 3))          # Works fine
hash((1, 2, [3, 4]))     # TypeError: unhashable type: 'list'
```

This is why tuples containing mutable items cannot be used as dict keys or set members.

## Flat Sequences Are Different

Unlike container sequences (tuples, lists, dicts), flat sequences like `str`, `bytes`, and `array.array` store their data directly in contiguous memory -- not as references. They are truly immutable in every sense.

## Key Takeaway

> A tuple's immutability protects its structure (which references it holds), not the objects those references point to. If a tuple contains a mutable item, the tuple's apparent value can change, and the tuple becomes unhashable.
