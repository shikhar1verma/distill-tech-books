---
title: "Higher-Order Functions"
book: "Fluent Python"
chapter: 7
tags: [higher-order-functions, functional-programming, sorted, map, filter]
related:
  - "[[first-class-functions]]"
  - "[[replacing-map-filter-reduce]]"
  - "[[anonymous-functions-lambda]]"
  - "[[replacing-map-filter-reduce]]"
---

# Higher-Order Functions

## Summary

A **higher-order function** is a function that takes a function as an argument or returns a function as its result (or both). Higher-order functions are a hallmark of functional programming and are deeply embedded in Python's standard library. The built-ins `sorted()`, `min()`, `max()`, `map()`, and `filter()` all accept a function argument. Writing your own higher-order functions unlocks powerful abstractions.

## How It Works

### Accepting a function as an argument

```python
fruits = ["strawberry", "fig", "apple", "cherry", "raspberry", "banana"]

# sorted() is a higher-order function — key= takes a function
print(sorted(fruits, key=len))
# ['fig', 'apple', 'cherry', 'banana', 'raspberry', 'strawberry']

# Custom key function
def reverse(word):
    return word[::-1]

print(sorted(fruits, key=reverse))
# ['banana', 'apple', 'fig', 'raspberry', 'strawberry', 'cherry']
```

### Returning a function as the result

```python
def make_multiplier(factor):
    def multiplier(x):
        return x * factor
    return multiplier          # returns a function

double = make_multiplier(2)
print(double(7))               # 14
```

### Classic higher-order functions

| Function | Takes a function? | Returns a function? |
|----------|:-:|:-:|
| `sorted(key=...)` | Yes | No |
| `map(func, iterable)` | Yes | No (returns iterator) |
| `filter(func, iterable)` | Yes | No (returns iterator) |
| `functools.partial(func, ...)` | Yes | Yes |

## In Practice

- **Sorting by complex criteria:** Pass `key=` functions to `sorted()`, `min()`, `max()`.
- **Applying transformations:** `map()` applies a function across all items. Prefer listcomps for clarity.
- **Factories:** Functions that return functions (closures) are used for configuration, memoization, and decorators.
- **Event-driven code:** Register callback functions that fire on events.

## Common Pitfalls

- **Using `map`/`filter` when a listcomp is clearer:** `[f(x) for x in items]` is almost always more readable than `list(map(f, items))`.
- **Forgetting that `map` and `filter` return iterators in Python 3:** You must wrap with `list()` to get a list.
- **Passing a method without binding:** `sorted(words, key=str.lower)` works; `sorted(words, key=lower)` does not (unless `lower` is defined).

## See Also

- [[first-class-functions]] -- Prerequisite: functions as objects
- [[replacing-map-filter-reduce]] -- Modern alternatives to classic HOFs
- [[anonymous-functions-lambda]] -- Creating inline function arguments
- [[replacing-map-filter-reduce]] -- `functools.partial` as a HOF
