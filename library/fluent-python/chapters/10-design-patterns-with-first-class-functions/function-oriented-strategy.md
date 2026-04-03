---
title: "Function-Oriented Strategy"
chapter: 10
concept_slug: function-oriented-strategy
book: "Fluent Python"
type: code-heavy
depends_on:
  - classic-strategy-pattern
tags:
  - design-patterns
  - strategy-pattern
  - first-class-functions
  - callable
---

# Function-Oriented Strategy

## Core idea

When a concrete strategy is a **stateless class with a single method**, replace it with a **plain function**. The Context accepts a `Callable` instead of a Strategy object.

## What changes from the [[classic-strategy-pattern]]

| Classic | Function-oriented |
|---------|-------------------|
| `Promotion` ABC with `discount()` method | No ABC needed |
| `FidelityPromo(Promotion)` class | `fidelity_promo(order)` function |
| `Order` holds `Optional[Promotion]` | `Order` holds `Optional[Callable[[Order], Decimal]]` |
| `self.promotion.discount(self)` | `self.promotion(self)` |
| Must instantiate: `FidelityPromo()` | Pass function directly: `fidelity_promo` |

## The refactored code

```python
from dataclasses import dataclass
from typing import Optional, Callable

@dataclass(frozen=True)
class Order:
    customer: Customer
    cart: Sequence[LineItem]
    promotion: Optional[Callable[['Order'], Decimal]] = None

    def due(self) -> Decimal:
        if self.promotion is None:
            discount = Decimal(0)
        else:
            discount = self.promotion(self)  # call the function directly
        return self.total() - discount
```

Strategies become plain functions:

```python
def fidelity_promo(order: Order) -> Decimal:
    """5% discount for customers with 1000 or more fidelity points"""
    if order.customer.fidelity >= 1000:
        return order.total() * Decimal('0.05')
    return Decimal(0)
```

Usage is simpler -- no instantiation needed:

```python
Order(ann, cart, fidelity_promo)   # pass the function itself
```

## Why `self.promotion(self)`?

`promotion` is an **instance attribute** that happens to be callable, not a method bound via the descriptor protocol. Python does not auto-bind it to `self`, so you must pass the `Order` instance explicitly. See "Methods Are Descriptors" (Chapter 23) for the full explanation.

## Why functions beat single-method classes here

1. **Less code**: no ABC, no class boilerplate, no `__init__`
2. **No Flyweight needed**: functions are created once at module load and shared naturally
3. **Composable**: functions can be stored in lists, passed to `max()`, decorated, etc.
4. **Readable**: the type hint `Callable[[Order], Decimal]` documents the interface

## When to keep classes

If a strategy needs **internal state** between calls (e.g., tracking cumulative purchases), a class or closure is appropriate. The function approach works for **stateless** algorithms.

## See also

- [[classic-strategy-pattern]] -- the pattern we are refactoring from
- [[choosing-best-strategy]] -- using function lists to pick the best strategy
- [[decorator-enhanced-strategy]] -- automatic registration of strategy functions
