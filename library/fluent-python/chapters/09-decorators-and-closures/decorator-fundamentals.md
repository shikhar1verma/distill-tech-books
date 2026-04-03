---
title: "Decorator Fundamentals"
slug: decorator-fundamentals
chapter: 9
book: "Fluent Python"
type: mixed
depends_on: []
tags:
  - decorators
  - import-time
  - registration
  - python
---

# Decorator Fundamentals

## Core Idea

A decorator is a callable that takes a function as its argument and returns a replacement (or the same) function. The `@decorator` syntax is syntactic sugar:

```python
@decorate
def target():
    print('running target()')

# is exactly equivalent to:
def target():
    print('running target()')
target = decorate(target)
```

## Three Essential Facts

1. **A decorator is a function or another callable.** Any object with `__call__` works.
2. **A decorator may replace the decorated function** with a different one (most do).
3. **Decorators are executed immediately when a module is loaded** (import time), not when the decorated function is called (runtime).

## Import Time vs. Runtime

This distinction is critical. When Python loads a module, every `@decorator` line runs the decorator function right then. The decorated functions themselves only run when explicitly called later.

```python
registry = []

def register(func):
    print(f'running register({func})')  # prints at IMPORT time
    registry.append(func)
    return func

@register
def f1():
    print('running f1()')  # prints only when f1() is called
```

If you `import` this module, you will see the `register` print output immediately -- before any of the registered functions are ever called.

## Registration Decorators

A **registration decorator** returns the decorated function unchanged. It just records the function somewhere (a list, dict, or set) as a side effect. This pattern is used heavily in web frameworks (URL routing), plugin systems, and event handlers.

In practice, the decorator is usually defined in one module and applied to functions in other modules.

## See Also

- [[variable-scope-and-closures]] -- closures are the mechanism that makes most decorators work
- [[implementing-decorators]] -- building a decorator that wraps behavior around the original function
