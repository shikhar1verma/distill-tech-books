---
title: "Data Class as Code Smell vs Scaffolding"
slug: data-class-as-code-smell
chapter: 5
book: "Fluent Python"
type: theory-heavy
depends_on:
  - dataclass-decorator-and-fields
tags: [code-smell, refactoring, OOP, design, scaffolding, serialization]
---

# Data Class as Code Smell vs Scaffolding

> *Data classes are like children. They are okay as a starting point, but to participate as a grownup object, they need to take some responsibility.*
> -- Martin Fowler & Kent Beck, *Refactoring*

## The Code Smell

In *Refactoring* (2nd ed.), Fowler and Beck catalog "Data Class" as a code smell:

> These are classes that have fields, getting and setting methods for fields, and nothing else. Such classes are dumb data holders and are often being manipulated in far too much detail by other classes.

A code smell is a **surface indication** that usually corresponds to a deeper problem. It does not always mean something is wrong -- "smells don't always indicate a problem" -- but it is worth investigating.

The core OOP principle at stake: **data and the functions that touch it should live together in the same class**. When a class has no significant behavior of its own, logic operating on its instances tends to scatter across the codebase -- a maintenance headache.

## The Refactoring Response

Fowler's approach:
1. Look at the data class and ask: *what behavior should be in this class?*
2. Start moving that behavior in (methods that operate on the fields)
3. The data class evolves into a class with real responsibility

## When Data Classes ARE Appropriate

### 1. Scaffolding

A data class as an **initial, simplistic implementation** to jump-start a project:

- Start with a bare `@dataclass` to get the structure right
- Gradually add methods as you understand the domain
- The scaffolding is temporary -- the class should eventually grow behavior

Python is also used for quick experimentation, where leaving the scaffolding in place is perfectly fine.

### 2. Intermediate Representation

A data class for **records crossing a system boundary** (import/export):

- Holding data just imported from JSON, CSV, database, API
- Building records about to be exported to an interchange format
- All three builders provide dict conversion (`_asdict()`, `asdict()`)

In this case, instances should be treated as **immutable** -- even if the fields are mutable, do not change them while they serve as intermediate representations. If transformation is needed, implement builder methods rather than mutating in place.

## Practical Guidance

| Situation | Recommendation |
|---|---|
| Quick prototype / script | Data class is fine as-is |
| Long-lived production class | Add behavior or refactor |
| Serialization boundary (JSON, DB) | Data class + `frozen=True` |
| Class used by many other classes | Move logic into the class |
| Pure value object (coordinates, money) | Data class with behavior is ideal |

## See Also

- [[dataclass-decorator-and-fields]] -- the technical details of `@dataclass`
- [[post-init-and-advanced-features]] -- adding behavior via `__post_init__`
- [[data-class-builders-overview]] -- choosing the right builder
