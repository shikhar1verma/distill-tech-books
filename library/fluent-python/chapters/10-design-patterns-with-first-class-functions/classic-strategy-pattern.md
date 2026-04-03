---
title: "Classic Strategy Pattern"
chapter: 10
concept_slug: classic-strategy-pattern
book: "Fluent Python"
type: mixed
depends_on: []
tags:
  - design-patterns
  - strategy-pattern
  - abc
  - oop
---

# Classic Strategy Pattern

## What it is

The **Strategy pattern** (from the Gang of Four's *Design Patterns*) defines a family of algorithms, encapsulates each one in its own class, and makes them interchangeable. The client (Context) delegates computation to a Strategy object without knowing which concrete algorithm is used.

## The three participants

| Role | In our example | Responsibility |
|------|---------------|----------------|
| **Context** | `Order` | Holds a reference to a Strategy and delegates discount calculation |
| **Strategy** (ABC) | `Promotion` | Declares the `discount()` interface |
| **Concrete Strategy** | `FidelityPromo`, `BulkItemPromo`, `LargeOrderPromo` | Implements a specific discount algorithm |

## E-commerce discount rules

- **FidelityPromo**: 5% off for customers with >= 1000 fidelity points
- **BulkItemPromo**: 10% off each line item with >= 20 units
- **LargeOrderPromo**: 7% off orders with >= 10 distinct items

## Code structure

```python
from abc import ABC, abstractmethod

class Promotion(ABC):
    @abstractmethod
    def discount(self, order: Order) -> Decimal:
        """Return discount as a positive dollar amount"""

class FidelityPromo(Promotion):
    def discount(self, order: Order) -> Decimal:
        if order.customer.fidelity >= 1000:
            return order.total() * Decimal('0.05')
        return Decimal(0)
```

The `Order` context is configured with a `Promotion` instance at creation time:

```python
Order(ann, cart, FidelityPromo())  # pass a concrete strategy instance
```

## The problem with this approach

Each concrete strategy is a **class with a single method** (`discount`) and **no instance state**. This is a lot of boilerplate for what is essentially just a function. In languages with first-class functions like Python, we can do better.

The GoF authors themselves noted this overhead and suggested the [[command-pattern-with-callables|Flyweight pattern]] to share strategy instances -- piling pattern upon pattern. Python's [[function-oriented-strategy]] eliminates the need entirely.

## Key takeaway

The classic Strategy pattern is a **valid starting point** for design, but in Python it is a stepping stone toward a simpler, function-based implementation. Recognize the pattern so you can refactor it.

## See also

- [[function-oriented-strategy]] -- the Pythonic replacement
- [[choosing-best-strategy]] -- selecting among multiple strategies
