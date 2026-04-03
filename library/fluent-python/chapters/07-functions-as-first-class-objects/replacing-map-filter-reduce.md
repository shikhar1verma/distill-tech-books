---
title: "Modern Replacements for map, filter, and reduce"
book: "Fluent Python"
chapter: 7
tags: [list-comprehension, generator-expression, map, filter, reduce, sum, functional-programming]
related:
  - "[[higher-order-functions]]"
  - "[[anonymous-functions-lambda]]"
  - "[[replacing-map-filter-reduce]]"
---

# Modern Replacements for map, filter, and reduce

## Summary

While `map()`, `filter()`, and `functools.reduce()` are available in Python, **list comprehensions and generator expressions** have largely replaced `map` and `filter` with clearer syntax. The `sum()` built-in replaces the most common use of `reduce()`. Other reducing built-ins include `all()` and `any()`. Use the functional tools only when they genuinely improve readability (rare).

## How It Works

### map/filter vs. list comprehension

```python
def factorial(n):
    return 1 if n < 2 else n * factorial(n - 1)

# map
list(map(factorial, range(6)))            # [1, 1, 2, 6, 24, 120]
# listcomp — same result, more readable
[factorial(n) for n in range(6)]          # [1, 1, 2, 6, 24, 120]

# map + filter + lambda
list(map(factorial, filter(lambda n: n % 2, range(6))))  # [1, 6, 120]
# listcomp with condition — no lambda needed
[factorial(n) for n in range(6) if n % 2]               # [1, 6, 120]
```

### reduce vs. sum

```python
from functools import reduce
from operator import add

reduce(add, range(100))   # 4950
sum(range(100))           # 4950  — clearer and faster
```

### Other reducing built-ins

```python
all([1, 2, 3])    # True  — no falsy elements
all([1, 0, 3])    # False — 0 is falsy
any([0, 0, 1])    # True  — at least one truthy
any([])            # False
```

## In Practice

- **Default to listcomps/genexps.** They handle transformation and filtering in one expression and avoid the need for `lambda`.
- **Use `sum()` for addition.** It is both more readable and faster than `reduce(add, ...)`.
- **`reduce()` still has niche uses:** When accumulating with a non-trivial two-argument function (e.g., building a nested structure). See `Vector.__hash__` in Chapter 12.
- **Generator expressions for large data:** `sum(x**2 for x in big_list)` avoids building an intermediate list.

## Common Pitfalls

- **`map` and `filter` return iterators in Python 3.** If you need a list, wrap with `list()`. Or better yet, use a listcomp.
- **`reduce` is no longer a built-in.** You must `from functools import reduce`.
- **Empty iterable edge cases:** `sum([])` returns `0`, `all([])` returns `True`, `any([])` returns `False`.
- **Performance myth:** `map()` is not always faster than a listcomp. In CPython, listcomps are heavily optimized.

## See Also

- [[higher-order-functions]] -- `map`, `filter`, `reduce` as higher-order functions
- [[anonymous-functions-lambda]] -- Lambdas often used (unnecessarily) with map/filter
- Chapter 17 covers generator expressions and iterators in depth
