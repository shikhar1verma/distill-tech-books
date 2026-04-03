---
title: "Reading Type Hints at Runtime"
book: "Fluent Python"
chapter: 15
tags: [python, type-hints, annotations, runtime, typing]
related:
  - "[[type-casting]]"
  - "[[typeddict]]"
  - "[[generic-classes]]"
---

# Reading Type Hints at Runtime

> **One-sentence summary.** Use `typing.get_type_hints()` (or `inspect.get_annotations()` in Python 3.10+) instead of reading `__annotations__` directly, because it resolves forward references and string annotations from postponed evaluation.

## How It Works

Python evaluates type hints at import time and stores them in `__annotations__` dictionaries on functions, classes, and modules:

```python
def clip(text: str, max_len: int = 80) -> str: ...

clip.__annotations__
# {'text': <class 'str'>, 'max_len': <class 'int'>, 'return': <class 'str'>}
```

This works when annotations are simple types. But two situations cause problems:

**1. Forward references.** When a method returns an instance of its own class, the class does not exist yet during class body evaluation. You must write the type as a string:

```python
class Rectangle:
    def stretch(self, factor: float) -> 'Rectangle':
        return Rectangle(width=self.width * factor)
```

Reading `__annotations__` gives you the string `'Rectangle'`, not the class.

**2. Postponed evaluation** (`from __future__ import annotations`). This PEP 563 feature stores ALL annotations as strings to reduce import-time CPU and memory cost. After this import, even `str` becomes the string `'str'` in `__annotations__`.

`typing.get_type_hints()` resolves both problems. It evaluates string annotations in the module's global/local namespace, turning `'Rectangle'` back into the `Rectangle` class:

```python
from typing import get_type_hints

get_type_hints(clip)
# {'text': <class 'str'>, 'max_len': <class 'int'>, 'return': <class 'str'>}
```

## In Practice

If you build frameworks or libraries that inspect type hints at runtime (like pydantic, FastAPI, or dataclass-like tools), always use `get_type_hints()` rather than `__annotations__`. Wrap it in a helper method so future API changes are localized:

```python
class Checked:
    @classmethod
    def _fields(cls) -> dict[str, type]:
        return get_type_hints(cls)
```

The rest of your codebase calls `_fields()` instead of `get_type_hints` directly. If the API changes (e.g., switching to `inspect.get_annotations` in Python 3.10+), you update one method.

The PEP 563 behavior (all annotations as strings) was planned to become the default in Python 3.10, but was postponed after the maintainers of pydantic and FastAPI showed it would break their runtime use of hints. PEP 649 proposes deferred evaluation using descriptors as an alternative. As of Python 3.12+, the situation is still evolving.

## Common Pitfalls

- **Never read `__annotations__` directly** in production code that must handle forward references or `from __future__ import annotations`.
- **`get_type_hints` has limits**: It cannot resolve all types in non-global contexts (inner classes, classes inside functions). For most standard use cases it works, but edge cases exist.
- **Import-time cost at scale**: Companies running Python at large scale care about the CPU/memory cost of evaluating annotations at import time. This tension between runtime users (pydantic) and performance-focused users is driving ongoing design changes.

## See Also

- [[type-casting]] -- `cast` also exists only for the type checker, but unlike annotations it has no runtime storage
- [[typeddict]] -- a construct whose annotations are only meaningful to the type checker
- [[generic-classes]] -- generic type parameters appear in annotations and must be resolved correctly
