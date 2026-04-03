---
title: "Anonymous Functions (lambda)"
book: "Fluent Python"
chapter: 7
tags: [lambda, anonymous-functions, functional-programming, refactoring]
related:
  - "[[first-class-functions]]"
  - "[[higher-order-functions]]"
  - "[[replacing-map-filter-reduce]]"
  - "[[replacing-map-filter-reduce]]"
---

# Anonymous Functions (lambda)

## Summary

The `lambda` keyword creates an anonymous function within a Python expression. The body is limited to a **single expression** -- no statements (`while`, `try`, `=` assignment) are allowed. Lambdas are most useful as short, throwaway callbacks in higher-order function calls like `sorted(key=...)`. If a lambda gets complex, refactor it into a named `def` function for readability and debuggability.

## How It Works

```python
# Basic lambda syntax
add = lambda a, b: a + b
print(add(3, 4))        # 7
print(add.__name__)     # '<lambda>'  — no meaningful name in tracebacks

# Best use: inline key function
fruits = ["strawberry", "fig", "apple", "cherry", "raspberry", "banana"]
sorted(fruits, key=lambda word: word[::-1])
# ['banana', 'apple', 'fig', 'raspberry', 'strawberry', 'cherry']
```

A `lambda` expression creates the exact same `function` object type as a `def` statement:

```python
print(type(lambda: None))  # <class 'function'>
```

### Lundh's Lambda Refactoring Recipe

If you find a lambda hard to understand:

1. Write a comment explaining what it does.
2. Think of a name that captures the essence of the comment.
3. Convert the `lambda` to a `def` using that name.
4. Remove the comment.

```python
# Before: obscure lambda
sorted(students, key=lambda s: (s.gpa, -s.age))

# After: clear named function
def gpa_then_youngest(student):
    return (student.gpa, -student.age)

sorted(students, key=gpa_then_youngest)
```

## In Practice

- **Sorting keys:** `sorted(items, key=lambda x: x.attr)` is the most common use.
- **Small callbacks:** `button.on_click(lambda: print("clicked"))` in GUI/event code.
- **Prefer `operator` functions:** `operator.itemgetter(1)` is clearer than `lambda x: x[1]`.
- **Prefer `functools.partial`:** `partial(mul, 3)` is clearer than `lambda x: 3 * x`.

## Common Pitfalls

- **Unreadable complex lambdas:** If it needs a comment, it needs a name. Use `def`.
- **Debugging difficulty:** Tracebacks show `<lambda>` instead of a meaningful function name.
- **Late binding in closures:** `lambda` captures variables by reference, not by value:
  ```python
  funcs = [lambda: i for i in range(3)]
  print([f() for f in funcs])  # [2, 2, 2]  — not [0, 1, 2]!
  # Fix: use default argument to capture the value
  funcs = [lambda i=i: i for i in range(3)]
  print([f() for f in funcs])  # [0, 1, 2]
  ```
- **No assignment in body:** `lambda x: x = 1` is a `SyntaxError`. The walrus operator `:=` technically works but signals your lambda is too complex.

## See Also

- [[higher-order-functions]] -- Lambdas are arguments to higher-order functions
- [[replacing-map-filter-reduce]] -- Cleaner alternatives to many lambdas
- [[replacing-map-filter-reduce]] -- Listcomps eliminate most map/filter lambdas
