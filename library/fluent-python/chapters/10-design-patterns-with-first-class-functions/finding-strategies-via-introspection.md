---
title: "Finding Strategies via Module Introspection"
chapter: 10
concept_slug: finding-strategies-via-introspection
book: "Fluent Python"
type: code-heavy
depends_on:
  - choosing-best-strategy
tags:
  - design-patterns
  - strategy-pattern
  - introspection
  - globals
  - inspect-module
---

# Finding Strategies via Module Introspection

## The problem

In [[choosing-best-strategy]], we manually maintained a `promos` list. Adding a new strategy function without updating the list is a silent bug.

## Approach A: `globals()` filtering

`globals()` returns the current module's global symbol table as a dict. We can filter it by naming convention:

```python
from strategy import Order
from strategy import fidelity_promo, bulk_item_promo, large_order_promo

promos = [promo for name, promo in globals().items()
          if name.endswith('_promo') and name != 'best_promo']

def best_promo(order: Order) -> Decimal:
    """Compute the best discount available"""
    return max(promo(order) for promo in promos)
```

Any function imported into the module whose name ends with `_promo` is automatically included. The filter excludes `best_promo` itself to avoid infinite recursion.

**Trade-off**: relies on a naming convention (`_promo` suffix). Static analysis tools will complain about "unused imports."

## Approach B: `inspect.getmembers()` on a dedicated module

Put all strategy functions in a separate `promotions` module, then introspect it:

```python
import inspect
import promotions

promos = [func for _, func in inspect.getmembers(promotions, inspect.isfunction)]

def best_promo(order: Order) -> Decimal:
    return max(promo(order) for promo in promos)
```

`inspect.getmembers(module, predicate)` returns `(name, value)` pairs filtered by the predicate. Using `inspect.isfunction` collects only function objects.

**Trade-off**: assumes every function in the `promotions` module is a valid strategy. A misplaced helper function would break `best_promo`.

## Modules are first-class objects too

Both approaches exploit the fact that **modules are objects** in Python, with attributes that can be introspected at runtime. This is the same principle as first-class functions, applied one level up.

## Limitations

- Both approaches are **implicit** -- the connection between a function and its role as a strategy is not visible at the function definition
- Naming conventions or module boundaries can be accidentally violated
- The [[decorator-enhanced-strategy]] solves these issues with explicit registration

## See also

- [[choosing-best-strategy]] -- the manual approach this improves upon
- [[decorator-enhanced-strategy]] -- the recommended solution
