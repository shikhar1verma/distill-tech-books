---
title: "Import Time Versus Runtime"
slug: import-time-vs-runtime
chapter: 24
book: fluent-python
type: theory-heavy
depends_on:
  - class-decorators
tags:
  - python
  - metaprogramming
  - evaluation-order
  - import-time
---

# Import Time Versus Runtime

## Core Idea

Python programmers talk about "import time" versus "runtime," but the boundary is fuzzy. Almost every Python statement is executable and can trigger user code. Understanding the exact order in which class-building code runs is essential for class metaprogramming.

## What Happens at Import Time

When Python imports a module, it:

1. **Parses** the source top-to-bottom (can raise `SyntaxError`)
2. **Compiles** to bytecode (or uses cached `.pyc`)
3. **Executes** all top-level code sequentially

"Top-level code" includes:
- `import` statements (which recursively trigger step 1-3 on other modules)
- Class bodies (the code inside a `class` block runs immediately)
- Decorator applications
- Module-level assignments and function calls

## The Class-Building Sequence

When Python encounters a `class` statement, the following steps execute **at import time**:

```
1. __prepare__(meta_cls, name, bases)     [metaclass only]
   --> returns the namespace mapping

2. Class body executes top-to-bottom
   --> populates the namespace

3. type.__new__(meta_cls, name, bases, namespace)
   --> creates the class object

4. __set_name__(self, owner, name)
   --> called on each descriptor in the class

5. __init_subclass__(subclass)
   --> called on the parent class

6. Class decorator applied
   --> receives and returns the class
```

Only instance creation and method invocation happen at "runtime."

## The `evaldemo` Experiment

The book demonstrates this with `builderlib.py` and `evaldemo.py`. When `evaldemo` is imported:

```
@ builderlib module start      # builderlib top-level
@ Builder body                  # class body of Builder
@ Descriptor body               # class body of Descriptor
@ builderlib module end         # builderlib top-level
# evaldemo module start         # evaldemo top-level
# Klass body                    # class body (step 2)
@ Descriptor.__init__           # descriptor created (step 2)
@ Descriptor.__set_name__       # (step 4)
@ Builder.__init_subclass__     # (step 5)
@ deco                          # decorator applied (step 6)
# evaldemo module end           # evaldemo top-level
```

No instances are created -- everything above is import-time activity.

## Why This Matters

- `__slots__` must be in the namespace **before** step 3, which is why only a metaclass (step 1) or a class factory function can configure it dynamically
- Descriptors get their owner class via `__set_name__` (step 4), so they can store metadata about the class they belong to
- `__init_subclass__` (step 5) sees a fully-constructed class but cannot undo what `type.__new__` already built
- Class decorators (step 6) run last and can override anything -- but the class has already been constructed

## Connections

- [[init-subclass]] -- fires at step 5
- [[class-decorators]] -- applied at step 6
- [[metaclasses]] -- `__prepare__` at step 1, `__new__` at step 3
- [[classes-as-objects]] -- the class object is created at step 3 and progressively enhanced through step 6
