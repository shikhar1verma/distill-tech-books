---
title: "Mutable Defaults and Defensive Programming"
slug: mutable-defaults-and-defensive-copy
chapter: 6
book: fluent-python
type: code-heavy
depends_on:
  - function-parameters-as-references
  - identity-equality-aliases
tags: [mutable-defaults, defensive-copy, None-sentinel, aliasing, bugs, best-practices]
---

# Mutable Defaults and Defensive Programming

## The Mutable Default Trap

Default parameter values are evaluated **once**, at function definition time (usually module import). The default object is stored as an attribute of the function object and reused on every call.

If the default is **mutable**, all calls that rely on it share the same object:

```python
class HauntedBus:
    def __init__(self, passengers=[]):   # BAD
        self.passengers = passengers

    def pick(self, name):
        self.passengers.append(name)
```

```python
bus1 = HauntedBus()
bus1.pick("Carrie")

bus2 = HauntedBus()          # uses the SAME default list
bus2.passengers               # ["Carrie"] -- ghost passenger!

bus1.passengers is bus2.passengers  # True
```

The shared default lives at:
```python
HauntedBus.__init__.__defaults__  # (["Carrie"],)
```

## The Fix: None Sentinel Pattern

```python
class GoodBus:
    def __init__(self, passengers=None):
        if passengers is None:
            self.passengers = []       # fresh list every time
        else:
            self.passengers = list(passengers)  # copy the argument
```

This is the standard Python idiom. It solves two problems at once:
1. No shared mutable default.
2. The caller's list is not aliased (defensive copy).

## Defensive Programming with Mutable Arguments

Even without mutable defaults, aliasing the caller's data is dangerous:

```python
class TwilightBus:
    def __init__(self, passengers=None):
        if passengers is None:
            self.passengers = []
        else:
            self.passengers = passengers  # BAD: alias, not copy

    def drop(self, name):
        self.passengers.remove(name)
```

```python
team = ["Sue", "Tina", "Maya", "Diana", "Pat"]
bus = TwilightBus(team)
bus.drop("Tina")
bus.drop("Pat")
team  # ["Sue", "Maya", "Diana"] -- Tina and Pat vanished from the team!
```

The bus is mutating the caller's list directly. This violates the **Principle of Least Astonishment**.

### The Fix

Always **copy** mutable arguments you intend to own:

```python
self.passengers = list(passengers)  # make a copy
```

This also gives you a bonus: the argument can be any iterable (tuple, set, generator), not just a list.

## When Aliasing Is Intentional

Sometimes you *want* to mutate the caller's object -- for example, `list.sort()` sorts in place by design. The key is to be **explicit** about intent:

- If you will mutate the argument, document it.
- If you will not mutate it, make a defensive copy.
- When in doubt, copy. The cost of a subtle aliasing bug far exceeds the cost of copying.

## Checklist

| Pattern | Safe? | Why |
|---------|-------|-----|
| `def f(items=[])` | No | Shared mutable default |
| `def f(items=None)` then `items = items or []` | Mostly | Breaks if caller passes empty list (falsy) |
| `def f(items=None)` then `if items is None: items = []` | Yes | Standard idiom |
| `self.data = data` (where data is a mutable arg) | No | Aliases caller's object |
| `self.data = list(data)` | Yes | Defensive copy |

## Key Takeaway

> Never use mutable objects as default parameter values. Use `None` as a sentinel and create a fresh object inside the function. When storing mutable arguments, always make a defensive copy to avoid aliasing the caller's data.
