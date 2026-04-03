---
title: "Methods Are Descriptors"
book: "Fluent Python"
chapter: 23
tags: [python, descriptors, methods, data-model, functions]
related:
  - "[[descriptor-protocol]]"
  - "[[overriding-vs-nonoverriding-descriptors]]"
  - "[[descriptor-usage-tips]]"
---

# Methods Are Descriptors

> **Python functions implement `__get__`, making them nonoverriding descriptors that return bound method objects when accessed through an instance.**

## How It Works

Every user-defined function in Python has a `__get__` method but no `__set__`. This makes functions **nonoverriding descriptors**. When a function is stored as a class attribute (which is what `def` inside a class body does), accessing it through an instance triggers the descriptor protocol:

- `obj.method` calls `function.__get__(obj, type(obj))`, which returns a **bound method** -- a callable that wraps the original function and binds `obj` as the first argument (`self`).
- `MyClass.method` calls `function.__get__(None, MyClass)`, which returns the function itself.

```python
import collections

class Text(collections.UserString):
    def reverse(self):
        return self[::-1]

word = Text('forward')

# Through instance: returns bound method
print(type(word.reverse))    # <class 'method'>

# Through class: returns function
print(type(Text.reverse))    # <class 'function'>

# They produce the same result
print(word.reverse())        # Text('drawrof')
print(Text.reverse(word))    # Text('drawrof')
```

A bound method object carries two key attributes:
- `__self__`: the instance it's bound to
- `__func__`: the original function

When you call the bound method, it internally calls `self.__func__(self.__self__, *args, **kwargs)`. This is how the implicit `self` parameter works in Python -- it's descriptor machinery, not syntax magic.

You can manually invoke the descriptor protocol to see this:

```python
# These three are equivalent:
word.reverse()
Text.reverse.__get__(word)()
Text.reverse(word)
```

## In Practice

Understanding that methods are descriptors explains several Python behaviors:

**Method shadowing**: Since functions have no `__set__`, you can shadow a method on a single instance by assigning to that attribute. `obj.method = lambda: 42` replaces the method for `obj` only, without affecting the class or other instances. This rarely happens by accident, but it's the mechanism behind some testing and monkey-patching patterns.

**Special methods are immune**: The interpreter looks up special methods (`__repr__`, `__len__`, etc.) on the class, not the instance. So `obj.__repr__ = lambda: 'custom'` has no effect on `repr(obj)`. This is a deliberate optimization in CPython.

**`staticmethod` and `classmethod`**: These are also descriptors. `staticmethod.__get__` returns the wrapped function without binding anything. `classmethod.__get__` returns a bound method where `__self__` is the class rather than the instance.

**Decorators as classes**: If you implement a decorator as a class with `__call__`, it works on plain functions. But if you use it on a method, you must also implement `__get__` so that accessing the decorated method through an instance correctly produces a bound method. Without `__get__`, the instance never gets passed as `self`.

## Common Pitfalls

- **Accidentally shadowing methods**: Assigning `self.method = value` in `__init__` (where `method` is also a regular method name) creates an instance attribute that hides the method. Use distinct names for data attributes and methods.
- **Class-based decorators missing `__get__`**: A callable class used as a method decorator must implement `__get__` to produce bound methods. Without it, `self` is never passed to the wrapped function.
- **Assuming `type(obj.method)` is `function`**: It's `method`. This matters when inspecting callables with `inspect.isfunction` vs `inspect.ismethod`.

## See Also

- [[descriptor-protocol]] -- the `__get__` method that powers this behavior
- [[overriding-vs-nonoverriding-descriptors]] -- functions are nonoverriding descriptors
- [[descriptor-usage-tips]] -- practical implications for your code
