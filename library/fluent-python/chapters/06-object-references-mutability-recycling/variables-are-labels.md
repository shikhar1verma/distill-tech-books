---
title: "Variables Are Labels, Not Boxes"
slug: variables-are-labels
chapter: 6
book: fluent-python
type: theory-heavy
depends_on: []
tags: [variables, references, assignment, binding, python-data-model]
---

# Variables Are Labels, Not Boxes

## Core Idea

In many introductory programming courses, variables are described as "boxes" that hold values. This mental model breaks down in Python (and every other language with reference semantics). The correct metaphor is **sticky notes**: a variable is a name label attached to an object that already exists in memory.

Assignment in Python does **not** copy data into a container. It **binds** a name to an object.

## How Assignment Works

```python
a = [1, 2, 3]   # 1. Create the list object [1, 2, 3]
                 # 2. Bind the name 'a' to that object

b = a            # Bind the name 'b' to the SAME object
```

After `b = a`, both `a` and `b` are labels on the same list. Mutating the list through either name is visible through the other:

```python
a.append(4)
print(b)  # [1, 2, 3, 4]
```

## Right-Hand Side First

The right-hand side of an assignment is always evaluated **before** the name is bound:

```python
class Gizmo:
    def __init__(self):
        print(f"Gizmo id: {id(self)}")

x = Gizmo()          # Object created, then 'x' is bound to it
y = Gizmo() * 10     # Object created, multiplication fails -> 'y' never exists
```

The second `Gizmo` is created (you see the print), but since `*` raises `TypeError`, the name `y` is never bound.

## Rebinding vs Mutating

These are fundamentally different operations:

| Operation | What happens | Example |
|-----------|-------------|---------|
| **Rebinding** | Name points to a new object | `a = [4, 5, 6]` |
| **Mutating** | The object itself changes | `a.append(4)` |

Rebinding one name never affects other names that pointed to the old object. Mutating the object is visible through all names attached to it.

## Why It Matters

- **Aliasing bugs**: If you think `b = a` copies a list, you will be surprised when mutating `a` also changes `b`.
- **Function arguments**: Parameters are bound to the same objects the caller passed -- not copies (see: call by sharing).
- **Immutables feel safe**: With `int`, `str`, `tuple`, rebinding is the only option, so the "box" metaphor happens to work. But it builds the wrong mental model for mutable objects.

## Key Takeaway

> Read assignment right-to-left: the object is created or retrieved on the right, then the name on the left is attached to it like a sticky note. The object can have many sticky notes (aliases). The object exists independently of any name.
