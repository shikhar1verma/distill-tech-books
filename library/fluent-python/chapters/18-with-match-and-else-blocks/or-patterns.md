---
title: "OR-patterns in match/case"
aliases: ["OR-pattern", "| pattern", "alternative patterns"]
tags: [fluent-python, chapter-18, pattern-matching, match-case, or-pattern]
chapter: 18
concept: 5
type: code-heavy
---

# OR-patterns in `match/case`

## Core Idea

Subpatterns joined by `|` form an **OR-pattern** that succeeds if **any** of the alternatives matches. All alternatives must bind the **same set of variables** so that the `case` body can use them regardless of which alternative matched.

## Syntax

```python
case pattern_a | pattern_b | pattern_c:
    # runs if any of the three patterns match
```

## Rules

1. **Any alternative succeeding is enough.** They are tried left to right.
2. **All alternatives must bind the same variable names.** This ensures the body always has the expected bindings.
3. **`|` in patterns is special syntax.** It does not trigger `__or__` or perform set union / bitwise OR.
4. **OR-patterns can be nested** inside larger patterns.

## Top-Level OR-pattern

```python
case int(x) | float(x):
    return x   # x is bound in both alternatives
```

## Nested OR-pattern

OR-patterns inside a sequence pattern:

```python
case ['lambda' | 'λ', [*parms], *body] if body:
    return Procedure(parms, body, env)
```

This matches either `'lambda'` or the Greek letter `'λ'` as the first element.

## Another Nested Example

```python
case [('yes' | 'on' | 'true'), *rest]:
    return True
case [('no' | 'off' | 'false'), *rest]:
    return False
```

## Invalid: Inconsistent Variable Bindings

```python
# This would be a SyntaxError:
case int(x) | str(y):   # ERROR: x vs y
    ...
```

All alternatives must use the same names. Fix:

```python
case int(x) | str(x):   # OK: both bind x
    ...
```

## Connections

- [[pattern-matching-beyond-sequences]] -- the broader context where OR-patterns are used in `lis.py`
