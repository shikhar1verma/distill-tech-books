---
title: "Function Parameters as References (Call by Sharing)"
slug: function-parameters-as-references
chapter: 6
book: fluent-python
type: code-heavy
depends_on:
  - variables-are-labels
tags: [call-by-sharing, parameters, arguments, mutability, functions, side-effects]
---

# Function Parameters as References (Call by Sharing)

## The Mechanism

Python's parameter passing mode is called **call by sharing** (also known as *call by object reference*). Each parameter inside the function receives a **copy of the reference** to the argument object. In other words, function parameters become **aliases** of the actual arguments.

This means:
- A function **can mutate** any mutable object it receives.
- A function **cannot replace** (rebind) the caller's variable.

## Demonstration

```python
def f(a, b):
    a += b
    return a
```

### With immutable types (no side effect)

```python
x, y = 1, 2
f(x, y)    # returns 3
x          # still 1 -- int is immutable, += created a new object

t, u = (10, 20), (30, 40)
f(t, u)    # returns (10, 20, 30, 40)
t          # still (10, 20) -- tuple is immutable
```

### With mutable types (side effect!)

```python
a = [1, 2]
b = [3, 4]
f(a, b)    # returns [1, 2, 3, 4]
a          # [1, 2, 3, 4] -- list was mutated in place by +=
```

The difference: `+=` on a list calls `list.__iadd__`, which extends the list **in place** and returns the same object. On immutable types, `+=` creates a **new** object and rebinds the local parameter -- the caller's variable is unaffected.

## Why Rebinding Does Not Escape

```python
def try_to_replace(items):
    items = [99, 100]    # rebinds LOCAL name, caller is unaffected

my_list = [1, 2, 3]
try_to_replace(my_list)
my_list                   # still [1, 2, 3]
```

The parameter `items` starts as an alias for `my_list`. But `items = [99, 100]` binds `items` to a new list -- it does not modify the original.

## The Two Rules

1. **If you mutate the parameter** (e.g., `.append()`, `.remove()`, `[i] = x`), the caller's object changes.
2. **If you rebind the parameter** (e.g., `param = new_value`), only the local name changes.

## Practical Implications

- If a function should not modify its arguments, work on a **copy**.
- If a function is *intended* to modify an argument (e.g., `list.sort()`), document this clearly and return `None` by convention.
- Prefer returning new objects over mutating arguments, when practical.

## Key Takeaway

> Python passes arguments by sharing references. Functions can mutate mutable arguments in place, but rebinding a parameter only affects the local name. Be deliberate about which of these two things your function does.
