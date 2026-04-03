---
title: "Tuples as Records and Immutable Lists"
book: "Fluent Python"
chapter: 2
tags: [tuple, immutability, records, hashable, sequences]
related:
  - "[[sequence-unpacking]]"
  - "[[augmented-assignment-sequences]]"
  - "[[pattern-matching-sequences]]"
---

## Summary

Tuples serve double duty in Python. As **records**, each position carries a specific meaning (e.g., `(latitude, longitude)`), and sorting or reordering would destroy information. As **immutable lists**, tuples provide clarity (length will not change), performance (less memory, faster construction), and hashability (when all contents are immutable), making them usable as dict keys and set members.

## How It Works

### Tuples as Records

Each item holds data for one field; position gives meaning:

```python
lax_coordinates = (33.9425, -118.408056)  # (latitude, longitude)
city, year, pop, chg, area = ('Tokyo', 2003, 32_450, 0.66, 8014)

traveler_ids = [('USA', '31195855'), ('BRA', 'CE342567')]
for country, _ in traveler_ids:
    print(country)
```

### Tuples as Immutable Lists

Performance advantages (per Raymond Hettinger):

1. **Bytecode**: A tuple literal is compiled as a single constant; a list literal pushes each element separately.
2. **No copy**: `tuple(t)` returns `t` itself if `t` is already a tuple.
3. **Exact allocation**: Tuples use exactly the memory needed. Lists over-allocate to amortize future appends.
4. **Cache-friendly**: Tuple item references are stored inline in the struct, avoiding an extra level of pointer indirection.

```python
import sys
t = tuple(range(100))
l = list(range(100))
print(sys.getsizeof(t))  # smaller
print(sys.getsizeof(l))  # larger -- room to spare
```

### The Immutability Caveat

Tuple immutability applies to the *references*, not the *objects* they point to. A tuple containing a list can appear to change:

```python
a = (10, 'alpha', [1, 2])
b = (10, 'alpha', [1, 2])
assert a == b
b[-1].append(99)
assert a != b  # b changed!
```

Use `hash()` to verify a tuple has a truly fixed value:

```python
def fixed(o):
    try:
        hash(o)
    except TypeError:
        return False
    return True

fixed((1, 2, (3, 4)))  # True
fixed((1, 2, [3, 4]))  # False
```

## In Practice

- Use tuples for **function return values** (e.g., `divmod()` returns `(quotient, remainder)`).
- Use tuples as **dict keys** or **set elements** when you need a composite key (only works if all items are hashable).
- Use tuples for **constant sequences** that should not be accidentally mutated.
- For records with named fields, consider `collections.namedtuple` or `typing.NamedTuple` (Chapter 5).

## Common Pitfalls

1. **Mutable items in tuples.** A tuple containing a list is not hashable and can change in surprising ways. Avoid this unless you have a specific reason.
2. **Assuming tuples are always safe as dict keys.** Only tuples whose items are all hashable can be used as keys.
3. **Confusing immutability with safety.** The references in a tuple cannot change, but the objects they point to can.

## See Also

- [[sequence-unpacking]] -- the primary way to extract fields from record-tuples
- [[augmented-assignment-sequences]] -- the `+=` puzzler with mutable items in tuples
- [[pattern-matching-sequences]] -- match/case destructures tuples declaratively
- Chapter 5 covers named tuples and dataclasses
- Chapter 6 covers references, mutability, and the "relative immutability of tuples"
