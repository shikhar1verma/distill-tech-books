---
title: "Type Casting with typing.cast"
book: "Fluent Python"
chapter: 15
tags: [python, type-hints, cast, typing]
related:
  - "[[overloaded-signatures]]"
  - "[[typeddict]]"
  - "[[runtime-type-hints]]"
---

# Type Casting with typing.cast

> **One-sentence summary.** `typing.cast(typ, val)` returns `val` completely unchanged at runtime but tells the type checker to treat the result as type `typ` -- it is a way to override the checker's inference when you know better.

## How It Works

No type system is perfect. Sometimes the checker cannot figure out the correct type, or the type stubs for a library are wrong or outdated. `typing.cast` provides an escape hatch.

Here is the actual implementation of `cast` in the `typing` module:

```python
def cast(typ, val):
    """Cast a value to a type.
    This returns the value unchanged."""
    return val
```

That is it -- a literal identity function. The type checker is required by PEP 484 to "blindly believe" the declared type. This makes `cast` useful for:

- Narrowing a type after an `isinstance` check the checker cannot follow
- Working around incorrect or outdated type stubs in third-party packages
- Documenting your type assumption explicitly in the code

```python
from typing import cast

def find_first_str(items: list[object]) -> str:
    index = next(i for i, x in enumerate(items) if isinstance(x, str))
    # Checker sees items[index] as 'object'; we know it is 'str'
    return cast(str, items[index])
```

## In Practice

A real-world scenario from the book: the `asyncio.Server.sockets` attribute was typed as `Optional[List[socket]]` on typeshed (correct for Python 3.6), but from Python 3.7+ the getter always returns a list (never `None`). A `cast` was needed to tell Mypy the value is a tuple of `TransportSocket`, not `Optional[List[socket]]`:

```python
from asyncio.trsock import TransportSocket
from typing import cast

socket_list = cast(tuple[TransportSocket, ...], server.sockets)
addr = socket_list[0].getsockname()
```

This required digging into undocumented internals to find the correct type -- a tradeoff between precision and effort.

## Common Pitfalls

- **Overuse is a code smell**: If you need many casts, your type design may need rethinking or your dependencies may have poor type coverage.
- **`cast` does not validate anything**: If you cast to the wrong type, the checker trusts you and you get bugs. It is a lie detector, not a lie preventer.
- **Prefer `cast` over alternatives**: `# type: ignore` is less informative, and using `Any` is contagious -- it disables checking for any expression derived from the `Any` value. `cast` is the least harmful option.
- **Sometimes `# type: ignore` is the only option**: Not all checker complaints can be fixed with `cast`. Use the right tool for the situation.

## See Also

- [[overloaded-signatures]] -- a complementary approach that avoids broad `Union` return types
- [[typeddict]] -- another construct that exists only for the type checker
- [[runtime-type-hints]] -- understanding how hints are stored and resolved
