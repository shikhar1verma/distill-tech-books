---
title: "List Comprehensions and Generator Expressions"
book: "Fluent Python"
chapter: 2
tags: [listcomp, genexp, sequences, iteration, lazy-evaluation]
related:
  - "[[tuples-as-records-and-immutable-lists]]"
  - "[[sequence-unpacking]]"
  - "[[augmented-assignment-sequences]]"
---

## Summary

List comprehensions (listcomps) build lists declaratively by applying an expression to each item from one or more iterables, with optional filtering. Generator expressions (genexps) use the same syntax wrapped in parentheses but yield items lazily, one at a time, saving memory when the result does not need to be a list.

## How It Works

### Listcomps

A listcomp replaces a multi-line `for` loop with a single readable expression. The intent -- "build a new list" -- is immediately obvious.

```python
# Traditional loop
symbols = '$\u00a2\u00a3\u00a5\u20ac\u00a4'
codes = []
for s in symbols:
    codes.append(ord(s))

# Listcomp equivalent
codes = [ord(s) for s in symbols]
```

**Filtering:** Add an `if` clause to select items:

```python
beyond_ascii = [ord(s) for s in symbols if ord(s) > 127]
```

This replaces `list(filter(lambda c: c > 127, map(ord, symbols)))` with clearer intent and often equal or better performance.

**Cartesian products:** Multiple `for` clauses produce nested iteration:

```python
colors = ['black', 'white']
sizes = ['S', 'M', 'L']
tshirts = [(c, s) for c in colors for s in sizes]
# Equivalent to nested for loops in the same order
```

### Genexps

Genexps use the same syntax but in parentheses. They yield items one at a time via the iterator protocol:

```python
# Feed a tuple constructor without building an intermediate list
t = tuple(ord(s) for s in symbols)

# Feed an array constructor
import array
a = array.array('I', (ord(s) for s in symbols))
```

When a genexp is the only argument to a function, the extra parentheses are not needed.

### Scope

In Python 3, listcomps, genexps, dict comps, and set comps all have their own local scope. The loop variable does not leak into the enclosing scope. However, variables assigned with the walrus operator `:=` do persist.

```python
x = 'ABC'
codes = [ord(x) for x in x]  # x is NOT clobbered
codes = [last := ord(c) for c in x]  # last IS accessible after
```

## In Practice

- Use a **listcomp** when you need the entire list.
- Use a **genexp** when feeding another constructor (`tuple()`, `set()`, `array.array()`) or iterating in a `for` loop -- avoids allocating a temporary list.
- For very large datasets, genexps can dramatically reduce peak memory usage.
- Cartesian-product listcomps replace deeply nested loops with a single readable expression.

## Common Pitfalls

1. **Using a listcomp for side effects only.** If you do not need the resulting list, use a regular `for` loop instead.
2. **Overly complex listcomps.** If it spans more than two lines or has multiple conditions, break it into a loop for clarity.
3. **Forgetting genexp parentheses.** When passing a genexp as one of multiple arguments, you must wrap it in its own parentheses: `array.array('I', (ord(s) for s in symbols))`.

## See Also

- [[tuples-as-records-and-immutable-lists]] -- genexps are ideal for building tuples
- [[augmented-assignment-sequences]] -- genexps feed array constructors efficiently
- Chapter 17 of Fluent Python covers generators in depth
