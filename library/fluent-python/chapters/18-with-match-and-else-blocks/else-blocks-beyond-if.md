---
title: "else Blocks Beyond if: for/while/try"
aliases: ["for/else", "while/else", "try/else", "EAFP", "LBYL"]
tags: [fluent-python, chapter-18, else-clause, for-else, try-else, EAFP]
chapter: 18
concept: 6
type: mixed
---

# `else` Blocks Beyond `if`

## Core Idea

Python allows `else` on `for`, `while`, and `try` statements. The semantics differ from `if/else`: here `else` means **"then"** (do this, *then* do that) rather than "otherwise."

## Rules

| Statement | `else` runs when... | `else` is skipped when... |
|-----------|---------------------|---------------------------|
| `for ... else` | Loop runs to completion (no `break`) | `break` was executed |
| `while ... else` | Condition becomes falsy (no `break`) | `break` was executed |
| `try ... else` | No exception raised in `try` block | An exception was raised |

In **all** cases, `else` is also skipped if `return`, `continue`, or an unhandled exception causes control to jump out of the main block.

## `for/else`: Search Pattern

The most common use: searching for an item and raising/handling when not found.

```python
for item in my_list:
    if item.flavor == 'banana':
        break
else:
    raise ValueError('No banana flavor found!')
```

The `else` block runs only if the loop exhausted the iterable without hitting `break`. This replaces the common pattern of setting a `found` flag.

## `while/else`

```python
while n > 0:
    n -= 1
else:
    print('Loop finished normally (condition became falsy)')
```

## `try/else`: Separating Guarded Code from Follow-Up

```python
try:
    dangerous_call()
except OSError:
    log('OSError...')
else:
    after_call()   # runs ONLY if no exception
```

**Why not just put `after_call()` inside the `try`?** Because:

1. It makes clear that `try` guards only `dangerous_call()`, not `after_call()`.
2. Exceptions from `after_call()` are **not** caught by the `except` clause.
3. It explicitly communicates that `after_call()` depends on `dangerous_call()` succeeding.

## EAFP vs LBYL

These acronyms from the Python glossary describe two coding styles:

### EAFP (Easier to Ask Forgiveness than Permission)

Assume things will work; handle exceptions if they don't. Characterized by `try/except/else`.

```python
try:
    value = mapping[key]
except KeyError:
    handle_missing()
else:
    process(value)
```

### LBYL (Look Before You Leap)

Check preconditions before acting. Characterized by `if` statements.

```python
if key in mapping:
    value = mapping[key]
    process(value)
else:
    handle_missing()
```

EAFP is generally preferred in Python because:
- It avoids **race conditions** in concurrent code (the key could be removed between the check and the access).
- It is often **faster** when the success path is common (no redundant lookup).

## Why `else` and Not `then`?

Ramalho notes that `then` would be a better keyword for these semantics, but adding a new keyword is a breaking change. The `else` keyword was reused for pragmatic reasons. For `match/case`, the wildcard `case _:` serves the role that `else` would play.

## Connections

- [[context-managers-and-with]] -- `with` replaces many `try/finally` patterns
- [[pattern-matching-beyond-sequences]] -- `case _:` serves as the `else` of `match`
