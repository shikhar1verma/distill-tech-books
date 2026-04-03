---
title: "Decorator-Enhanced Strategy Pattern"
chapter: 10
concept_slug: decorator-enhanced-strategy
book: "Fluent Python"
type: code-heavy
depends_on:
  - finding-strategies-via-introspection
tags:
  - design-patterns
  - strategy-pattern
  - decorators
  - registration-decorator
---

# Decorator-Enhanced Strategy Pattern

## The cleanest solution

A **registration decorator** appends each strategy function to the `promos` list at definition time. No naming conventions, no introspection -- fully explicit.

## Implementation

```python
Promotion = Callable[['Order'], Decimal]

promos: list[Promotion] = []

def promotion(promo: Promotion) -> Promotion:
    """Registration decorator: appends promo to the global list."""
    promos.append(promo)
    return promo  # returns the function unchanged
```

Define strategies with the decorator:

```python
@promotion
def fidelity(order: Order) -> Decimal:
    """5% discount for customers with 1000+ fidelity points"""
    if order.customer.fidelity >= 1000:
        return order.total() * Decimal('0.05')
    return Decimal(0)

@promotion
def bulk_item(order: Order) -> Decimal:
    """10% discount for each LineItem with 20+ units"""
    discount = Decimal(0)
    for item in order.cart:
        if item.quantity >= 20:
            discount += item.total() * Decimal('0.1')
    return discount

@promotion
def large_order(order: Order) -> Decimal:
    """7% discount for orders with 10+ distinct items"""
    distinct_items = {item.product for item in order.cart}
    if len(distinct_items) >= 10:
        return order.total() * Decimal('0.07')
    return Decimal(0)
```

`best_promo` is unchanged -- it relies on the `promos` list:

```python
def best_promo(order: Order) -> Decimal:
    return max(promo(order) for promo in promos)
```

## How the decorator works

This is a **registration decorator** (covered in Chapter 9, "Registration Decorators"). It does not wrap or modify the function -- it simply records it in a list and returns it unchanged. The decorator runs at **import time** (when the module is loaded), so `promos` is populated before any orders are created.

## Advantages over previous approaches

| Approach | Weakness | Decorator solves it? |
|----------|----------|---------------------|
| Manual `promos` list | Forget to add new functions | Yes -- `@promotion` auto-registers |
| `globals()` filtering | Relies on naming convention | Yes -- any name works |
| `inspect.getmembers()` | Relies on module boundaries | Yes -- works cross-module |
| All implicit approaches | Intent not visible at definition | Yes -- `@promotion` is self-documenting |

## Additional benefits

- **Easy to toggle**: comment out `@promotion` to temporarily disable a strategy
- **Cross-module**: strategies can be defined anywhere, as long as they apply `@promotion`
- **Type-safe**: the `Promotion` type alias documents the expected callable signature

## Key takeaway

Registration decorators are a simple, powerful pattern for building plugin-like systems. The decorator is trivial (3 lines), but it eliminates an entire class of silent bugs.

## See also

- [[finding-strategies-via-introspection]] -- the approaches this improves upon
- [[function-oriented-strategy]] -- the foundation: strategies as functions
- [[choosing-best-strategy]] -- the `best_promo` meta-strategy
