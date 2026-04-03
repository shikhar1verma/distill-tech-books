---
title: "Special (Dunder) Methods"
book: "Fluent Python"
chapter: 1
tags: [python, data-model, dunder-methods, special-methods, metaobject-protocol]
related:
  - "[[sequence-protocol-french-deck]]"
  - "[[numeric-type-emulation]]"
  - "[[string-representation]]"
  - "[[boolean-value-custom-types]]"
  - "[[collection-api-abcs]]"
---

## Summary

Special methods (also called **dunder methods** or informally **magic methods**) are the foundation of the Python Data Model. They are methods with names surrounded by double underscores -- like `__len__`, `__getitem__`, `__repr__`, and `__add__` -- that the Python interpreter calls implicitly when you use built-in functions, operators, or language syntax on your objects. By implementing these methods, your custom classes integrate seamlessly with Python's built-in features.

The term "dunder" is short for "double underscore before and after." You say `__getitem__` as "dunder-getitem."

## How It Works

The Python Data Model works as an **inversion of control** pattern: you define special methods on your class, and the Python *framework* (the interpreter) calls them at the right time. You almost never call them directly.

```python
# YOU implement special methods:
class Deck:
    def __init__(self):
        self._cards = list(range(52))

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]

# The INTERPRETER calls them via built-in functions and syntax:
d = Deck()
len(d)       # interpreter calls d.__len__()
d[0]         # interpreter calls d.__getitem__(0)
5 in d       # interpreter uses d.__getitem__ to iterate and check
```

When you write `len(d)`, Python does not simply call `d.__len__()`. For built-in types like `list` and `str`, CPython reads the length directly from a C struct field (`ob_size`), bypassing the method call entirely. This is why `len()` is a function and not a method -- it is a performance optimization baked into the language.

The special method mechanism covers nearly every aspect of the language:

| Category | Example methods |
|----------|----------------|
| String/bytes representation | `__repr__`, `__str__`, `__format__`, `__bytes__` |
| Numeric operations | `__add__`, `__mul__`, `__abs__`, `__neg__` |
| Collections | `__len__`, `__getitem__`, `__setitem__`, `__contains__` |
| Iteration | `__iter__`, `__next__`, `__reversed__` |
| Context management | `__enter__`, `__exit__` |
| Attribute access | `__getattr__`, `__setattr__`, `__delattr__` |
| Callable objects | `__call__` |
| Object lifecycle | `__new__`, `__init__`, `__del__` |

The Python Language Reference documents more than 80 special method names.

## In Practice

The most common special methods you will implement in everyday code are:

- `__init__` -- object initialization (you call `super().__init__()` directly; this is the one exception)
- `__repr__` -- developer-facing string representation
- `__len__` and `__getitem__` -- to make your class behave like a sequence
- `__eq__` and `__hash__` -- for equality comparison and use in sets/dicts
- `__enter__` and `__exit__` -- for context managers (`with` statements)
- `__iter__` and `__next__` -- for custom iterators

When you implement special methods, your objects gain access to the entire Python ecosystem: `sorted()`, `reversed()`, `random.choice()`, unpacking, `for` loops, f-strings, and more. This is the core bargain of the Python Data Model -- you write a few methods, and the language gives you a lot in return.

## Common Pitfalls

1. **Calling dunder methods directly.** Write `len(obj)`, not `obj.__len__()`. The built-in functions may be faster and provide additional behavior.

2. **Inventing your own dunder names.** Names like `__*__` are reserved by the language. Never create custom methods with this naming pattern -- they may collide with future Python versions.

3. **Forgetting that special methods are looked up on the type, not the instance.** Python calls `type(obj).__len__(obj)`, not `obj.__len__()`. This means you cannot override a special method by assigning to an instance attribute.

4. **Implementing `__str__` without `__repr__`.** If you only implement one, choose `__repr__`. The `object.__str__` default falls back to `__repr__`, but the reverse is not true.

5. **Not returning `NotImplemented` from binary operators.** If your `__add__` cannot handle the other operand's type, return `NotImplemented` (not raise `NotImplementedError`) so Python can try the reflected method on the other operand.

## See Also

- [[sequence-protocol-french-deck]] -- Practical example of `__getitem__` and `__len__`
- [[numeric-type-emulation]] -- Practical example of `__add__`, `__mul__`, `__abs__`
- [[string-representation]] -- Deep dive into `__repr__` vs `__str__`
- [[boolean-value-custom-types]] -- How `__bool__` and `__len__` control truthiness
- [[collection-api-abcs]] -- The abstract base classes that formalize collection interfaces
