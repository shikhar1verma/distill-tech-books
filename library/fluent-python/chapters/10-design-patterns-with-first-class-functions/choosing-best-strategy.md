---
title: "Choosing the Best Strategy"
chapter: 10
concept_slug: choosing-best-strategy
book: "Fluent Python"
type: code-heavy
depends_on:
  - function-oriented-strategy
tags:
  - design-patterns
  - strategy-pattern
  - first-class-functions
  - higher-order-functions
---

# Choosing the Best Strategy

## The idea

Once strategies are plain functions, it is natural to store them in a **list** and write a **meta-strategy** (`best_promo`) that tries all of them and returns the maximum discount.

## Implementation

```python
promos = [fidelity_promo, bulk_item_promo, large_order_promo]

def best_promo(order: Order) -> Decimal:
    """Compute the best discount available"""
    return max(promo(order) for promo in promos)
```

`best_promo` is itself a valid promotion function (same signature), so it plugs into `Order` just like any other strategy:

```python
Order(joe, long_cart, best_promo)   # automatically picks the best discount
```

## Why this works

- Functions are **first-class objects** -- they can be stored in lists, passed to `max()`, iterated over
- A generator expression `(promo(order) for promo in promos)` lazily evaluates each strategy
- `best_promo` has the same signature as any single strategy, so it is **composable** with the Context

## The maintenance problem

There is a subtle bug risk: if you add a new promotion function but forget to add it to the `promos` list, `best_promo` silently ignores it. The function will work when passed directly to `Order`, but `best_promo` will never consider it.

This duplication (define the function, then remember to register it) is solved by:

1. [[finding-strategies-via-introspection]] -- automatic discovery via `globals()` or `inspect`
2. [[decorator-enhanced-strategy]] -- a registration decorator (the cleanest approach)

## Key takeaway

Storing functions in data structures is a natural consequence of first-class functions. When you see yourself building a list of strategy objects, ask: "Can these be a list of functions instead?"

## See also

- [[function-oriented-strategy]] -- the prerequisite refactoring
- [[finding-strategies-via-introspection]] -- solving the maintenance problem
- [[decorator-enhanced-strategy]] -- the cleanest solution
