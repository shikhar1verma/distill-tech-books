---
title: "Pattern Matching Beyond Sequences: The lis.py Case Study"
aliases: ["match/case advanced", "class patterns", "lis.py", "Scheme interpreter"]
tags: [fluent-python, chapter-18, pattern-matching, match-case, interpreter]
chapter: 18
concept: 4
type: mixed
---

# Pattern Matching Beyond Sequences: The `lis.py` Case Study

## Core Idea

Chapter 18 uses Peter Norvig's `lis.py` -- a Scheme interpreter in Python -- to demonstrate that `match/case` goes far beyond simple switch statements. The `evaluate` function at the heart of the interpreter uses **class patterns**, **sequence patterns with guards**, **OR-patterns**, and **nested destructuring** to express the grammar of a language with remarkable clarity.

## Pattern Types Demonstrated

### Class Patterns

Match by type and capture the value:

```python
case int(x) | float(x):
    return x         # number literal

case Symbol(var):
    return env[var]  # variable lookup
```

For built-in types (`int`, `float`, `str`), the class pattern captures the value itself. For custom classes, it matches against `__match_args__`.

### Sequence Patterns with Guards

Destructure a list and add a boolean condition:

```python
case ['lambda', [*parms], *body] if body:
    return Procedure(parms, body, env)
```

The guard `if body` ensures the body is non-empty. Without it, `['lambda', []]` would match with `body = []`.

### Nested Destructuring

Patterns can reach into nested structures:

```python
case ['define', [Symbol(name), *parms], *body] if body:
    env[name] = Procedure(parms, body, env)
```

This matches a list like `['define', ['average', 'a', 'b'], ['/', ['+', 'a', 'b'], 2]]`, binding `name='average'`, `parms=['a', 'b']`, and `body` to the remaining expressions.

### Wildcard / Catch-All

```python
case _:
    raise SyntaxError(lispstr(exp))
```

## The `evaluate` Function (Simplified)

```python
KEYWORDS = ['quote', 'if', 'lambda', 'define', 'set!']

def evaluate(exp, env):
    match exp:
        case int(x) | float(x):           return x
        case Symbol(var):                  return env[var]
        case ['quote', x]:                 return x
        case ['if', test, con, alt]:
            return evaluate(con if evaluate(test, env) else alt, env)
        case ['lambda', [*parms], *body] if body:
            return Procedure(parms, body, env)
        case ['define', Symbol(name), value_exp]:
            env[name] = evaluate(value_exp, env)
        case ['define', [Symbol(name), *parms], *body] if body:
            env[name] = Procedure(parms, body, env)
        case ['set!', Symbol(name), value_exp]:
            env.change(name, evaluate(value_exp, env))
        case [func_exp, *args] if func_exp not in KEYWORDS:
            proc = evaluate(func_exp, env)
            values = [evaluate(arg, env) for arg in args]
            return proc(*values)
        case _:
            raise SyntaxError(lispstr(exp))
```

Each `case` clause maps directly to a Scheme syntactic form. The patterns express both the **structure** (what the expression looks like) and the **semantics** (what to do with the captured parts).

## Key Insight: Why Guards Matter

The guard on the function call case (`if func_exp not in KEYWORDS`) prevents misinterpreting a malformed keyword expression as a function call. Without it, `(lambda is not like this)` would attempt to call `lambda` as a function instead of raising `SyntaxError`.

## The `Procedure` Class: Closures Revealed

```python
class Procedure:
    def __init__(self, parms, body, env):
        self.parms = parms
        self.body = body
        self.env = env     # captured environment = closure

    def __call__(self, *args):
        local_env = dict(zip(self.parms, args))
        env = Environment(local_env, self.env)
        for exp in self.body:
            result = evaluate(exp, env)
        return result
```

A closure stores the **environment at definition time**. When called, it creates a new local scope chained to the captured environment.

## Connections

- [[or-patterns]] -- the `|` syntax used in `case int(x) | float(x):`
- [[else-blocks-beyond-if]] -- the `else` clause in Python control flow
