---
title: "The super() Function"
book: "Fluent Python"
chapter: 14
tags: [python, oop, inheritance, super]
related:
  - "[[multiple-inheritance-mro]]"
  - "[[cooperative-multiple-inheritance]]"
  - "[[mixin-classes]]"
---

# The super() Function

> **One-sentence summary.** `super()` returns a dynamic proxy object that delegates method calls to the next class in the Method Resolution Order (MRO), enabling correct method dispatch in both single and multiple inheritance hierarchies.

## How It Works

When a subclass overrides a method, it often needs to call the original version from a parent class. `super()` provides the standard way to do this. In Python 3, calling `super()` with no arguments is equivalent to `super(CurrentClass, self)` — the bytecode compiler fills in both arguments automatically by inspecting the surrounding context.

The proxy returned by `super()` looks up the method in the next class listed in the MRO of the receiver's type, not just the immediate parent. This distinction matters in single inheritance (where the two happen to be the same), but becomes critical in multiple inheritance hierarchies.

```python
from collections import OrderedDict

class LastUpdatedOrderedDict(OrderedDict):
    """Store items in the order they were last updated."""

    def __setitem__(self, key, value):
        super().__setitem__(key, value)  # delegates to OrderedDict
        self.move_to_end(key)

d = LastUpdatedOrderedDict()
d['a'] = 1
d['b'] = 2
d['a'] = 10  # 'a' moves to the end
print(list(d.items()))  # [('b', 2), ('a', 10)]
```

### The two arguments of super()

`super(type, object_or_type)` takes:
- **type**: the starting point for the MRO search (the class owning the method where `super()` appears)
- **object_or_type**: the receiver (`self` for instance methods, the class for class methods)

In Python 2, you had to supply both explicitly: `super(LastUpdatedOrderedDict, self).__setitem__(key, value)`. Python 3 makes them optional.

## In Practice

**Always use `super()` instead of hardcoding the parent class name.** Hardcoding is fragile — if the base class changes, every call site must be updated:

```python
# Anti-pattern: hardcoded superclass
class NotRecommended(OrderedDict):
    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)  # fragile!
        self.move_to_end(key)
```

Beyond fragility, hardcoding bypasses the MRO entirely. In a multiple inheritance hierarchy, this means sibling classes are silently skipped, breaking cooperative method dispatch.

**Always call `super().__init__()` in `__init__`.** Unlike Java, Python does not automatically invoke the parent constructor. Forgetting this is a common source of bugs, especially when a superclass sets up essential instance state.

## Common Pitfalls

- **Forgetting to call super().__init__()**: Python won't warn you. The instance simply won't have attributes the parent was supposed to set up, leading to AttributeError later.
- **Hardcoding the parent name**: Works for simple cases but silently breaks multiple inheritance and makes refactoring error-prone.
- **Providing only one argument**: `super(ClassName)` without the second argument returns an unbound super object, which is almost never useful and may be deprecated.

## See Also

- [[multiple-inheritance-mro]] — how the MRO determines which class `super()` delegates to
- [[cooperative-multiple-inheritance]] — why every method should call `super()` for correct chain traversal
- [[mixin-classes]] — practical pattern that depends on `super()` for method delegation
