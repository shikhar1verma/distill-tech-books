---
title: "Sequence and Iterable Unpacking"
book: "Fluent Python"
chapter: 2
tags: [unpacking, parallel-assignment, star-expression, destructuring, sequences]
related:
  - "[[tuples-as-records-and-immutable-lists]]"
  - "[[pattern-matching-sequences]]"
  - "[[list-comprehensions-genexps]]"
---

## Summary

Unpacking (also called iterable unpacking) lets you assign elements from any iterable to multiple variables in a single statement, eliminating error-prone indexing. Python supports parallel assignment, star expressions (`*rest`) for grabbing excess items, nested unpacking for hierarchical data, and the `*` operator in function calls and literals (PEP 448).

## How It Works

### Parallel Assignment

The most common form: assign each item of an iterable to a corresponding variable.

```python
latitude, longitude = (33.9425, -118.408056)

# Classic swap without temp variable
a, b = b, a

# Unpack function return values
quotient, remainder = divmod(20, 8)
```

### Using `*` to Grab Excess Items

A single starred variable captures remaining items as a list. It can appear in any position:

```python
a, b, *rest = range(5)       # rest = [2, 3, 4]
a, *body, c, d = range(5)    # body = [1, 2]
*head, b, c, d = range(5)    # head = [0, 1]
```

The starred variable always produces a `list`, which may be empty:

```python
a, b, *rest = range(2)       # rest = []
```

### Nested Unpacking

Unpacking works on nested structures if the target mirrors the data shape:

```python
metro_areas = [
    ('Tokyo', 'JP', 36.933, (35.689722, 139.691667)),
    ('Mexico City', 'MX', 20.142, (19.433333, -99.133333)),
]

for name, _, _, (lat, lon) in metro_areas:
    print(f"{name}: {lat}, {lon}")
```

### `*` in Function Calls and Literals (PEP 448)

Python 3.5+ allows multiple `*` unpacking in calls and literals:

```python
# Multiple * in function calls
def fun(a, b, c, d, *rest):
    return a, b, c, d, rest

fun(*[1, 2], 3, *range(4, 7))  # (1, 2, 3, 4, (5, 6))

# * in list/tuple/set literals
[*range(4), 4]              # [0, 1, 2, 3, 4]
{*range(4), *(5, 6, 7)}     # {0, 1, 2, 3, 5, 6, 7}
```

### Using `_` as Dummy Variable

By convention, `_` signals "I don't care about this value":

```python
_, filename = os.path.split('/home/user/.ssh/id_rsa.pub')
```

Note: in `match/case`, `_` is a true wildcard that is never bound.

## In Practice

- Use unpacking to **avoid indexing** -- `name, age = record` is clearer than `name = record[0]`.
- Use `*rest` to handle **variable-length sequences** (e.g., first/last elements of unknown-length data).
- Use nested unpacking for **hierarchical data** like coordinate pairs inside records.
- Use `_` for values you intentionally ignore to signal intent to readers.

## Common Pitfalls

1. **Mismatched count.** If the iterable has more or fewer items than variables (and no `*`), you get `ValueError`.
2. **`*` can only appear once** per target level. `a, *b, *c = ...` is a `SyntaxError`.
3. **Confusing `_` convention with `match/case` wildcard.** In regular code, `_` is a normal variable (it holds the value). In `match/case`, `_` never binds.
4. **Single-item tuple unpacking.** `(record,) = query()` requires the trailing comma. Forgetting it is a silent bug.

## See Also

- [[tuples-as-records-and-immutable-lists]] -- the primary data structure unpacking extracts from
- [[pattern-matching-sequences]] -- `match/case` extends unpacking with type checks and guards
- PEP 3132 -- Extended Iterable Unpacking (the `*` in assignment)
- PEP 448 -- Additional Unpacking Generalizations (multiple `*` in calls and literals)
