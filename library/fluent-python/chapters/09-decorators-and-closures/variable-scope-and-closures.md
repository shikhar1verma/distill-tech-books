---
title: "Variable Scope Rules and Closures"
slug: variable-scope-and-closures
chapter: 9
book: "Fluent Python"
type: mixed
depends_on:
  - decorator-fundamentals
tags:
  - scope
  - closures
  - free-variables
  - python
---

# Variable Scope Rules and Closures

## Variable Scope Rules

Python determines variable scope at **compile time**, not at runtime. The rule is simple but surprising:

> If a variable is **assigned anywhere** in a function body, Python treats it as **local to the entire function** -- even before the assignment line.

```python
b = 6
def f2(a):
    print(a)
    print(b)   # UnboundLocalError! b is local because of the line below
    b = 9
```

This is a deliberate design choice, not a bug. Python avoids JavaScript's problem where forgetting `var` silently clobbers globals.

### Variable Lookup Logic

When Python compiles a function, it determines how to fetch each variable `x`:

1. If `global x` is declared: look in the module global scope.
2. If `nonlocal x` is declared: look in the nearest enclosing function scope.
3. If `x` is a parameter or assigned in the body: it is **local**.
4. Otherwise, search outward: enclosing function scopes, then module globals, then `__builtins__`.

## Closures

A **closure** is a function that retains bindings for **free variables** -- variables that are not local and not global, but come from the enclosing function's scope.

```python
def make_averager():
    series = []          # local to make_averager

    def averager(new_value):
        series.append(new_value)  # series is a FREE variable
        return sum(series) / len(series)

    return averager
```

When `make_averager()` returns, its local scope is gone. But `averager` keeps a reference to `series` through its closure.

### Inspecting a Closure

```python
avg = make_averager()
avg.__code__.co_freevars   # ('series',)
avg.__closure__[0].cell_contents  # [10, 11, 12] after three calls
```

- `__code__.co_freevars` lists the names of free variables.
- `__closure__` holds `cell` objects, each with a `cell_contents` attribute storing the actual value.

### Why Closures Matter

Closures are the mechanism that makes decorators with inner wrapper functions work. The inner function captures `func` (the decorated function) as a free variable. Without closures, decorators would have no way to remember which function they are wrapping.

## See Also

- [[nonlocal-declaration]] -- what to do when you need to rebind a free variable
- [[decorator-fundamentals]] -- where closures are put to practical use
