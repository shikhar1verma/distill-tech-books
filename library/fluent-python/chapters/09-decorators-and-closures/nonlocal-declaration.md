---
title: "The nonlocal Declaration"
slug: nonlocal-declaration
chapter: 9
book: "Fluent Python"
type: code-heavy
depends_on:
  - variable-scope-and-closures
tags:
  - nonlocal
  - closures
  - scope
  - python
---

# The nonlocal Declaration

## The Problem

If a closure captures a mutable object (like a list), you can call methods on it without issues -- `series.append(x)` does not rebind `series`. But if the free variable holds an **immutable** value (int, str, tuple), any attempt to update it with `+=` or `=` creates a new **local** variable, breaking the closure.

```python
def make_averager():
    count = 0
    total = 0

    def averager(new_value):
        count += 1          # count = count + 1 --> makes count LOCAL
        total += new_value   # same problem
        return total / count

    return averager
```

Calling `make_averager()(10)` raises `UnboundLocalError: local variable 'count' referenced before assignment`.

## The Fix: nonlocal

The `nonlocal` keyword (introduced in Python 3.0) declares that a variable lives in the enclosing scope, allowing assignment without creating a local:

```python
def make_averager():
    count = 0
    total = 0

    def averager(new_value):
        nonlocal count, total  # <-- the fix
        count += 1
        total += new_value
        return total / count

    return averager
```

Now `count` and `total` are properly treated as free variables and the closure works.

## When Do You Need nonlocal?

| Operation | Needs nonlocal? | Why |
|---|---|---|
| `series.append(x)` | No | Mutating the object, not rebinding the name |
| `count += 1` | **Yes** | Rebinds `count` to a new int object |
| `name = "new"` | **Yes** | Rebinds `name` to a new str object |
| `d["key"] = val` | No | Mutating the dict, not rebinding `d` |

The rule: **nonlocal is needed only when you rebind (assign to) an immutable free variable.**

## nonlocal vs. global

- `global x`: declares `x` lives in the **module** scope.
- `nonlocal x`: declares `x` lives in the **nearest enclosing function** scope.

Python does not have a program-wide global scope -- `global` always means module-level.

## See Also

- [[variable-scope-and-closures]] -- the scope rules that create this problem
- [[implementing-decorators]] -- nonlocal is commonly needed inside decorator wrappers
