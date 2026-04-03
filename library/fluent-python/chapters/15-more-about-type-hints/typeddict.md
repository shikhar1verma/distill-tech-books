---
title: "TypedDict for Typed Dictionaries"
book: "Fluent Python"
chapter: 15
tags: [python, type-hints, typeddict, typing]
related:
  - "[[overloaded-signatures]]"
  - "[[type-casting]]"
  - "[[runtime-type-hints]]"
---

# TypedDict for Typed Dictionaries

> **One-sentence summary.** `typing.TypedDict` annotates dictionaries used as records with per-key value types, but it produces plain dicts at runtime and provides zero enforcement -- only static type checkers use the information.

## How It Works

Python dicts are sometimes used as lightweight records where each key is a field name and values have different types. Before `TypedDict` (PEP 589, Python 3.8), there was no way to express "this dict has key `isbn` of type `str` and key `pagecount` of type `int`." The best you could do was `Dict[str, Any]` or a clumsy `Union`.

`TypedDict` uses class syntax to define the expected keys and their types:

```python
from typing import TypedDict

class BookDict(TypedDict):
    isbn: str
    title: str
    authors: list[str]
    pagecount: int

book = BookDict(isbn="0134757599", title="Refactoring", authors=["Fowler"], pagecount=478)
# book is a plain dict -- type(book) is <class 'dict'>
```

The type checker will:
- Flag assignments of wrong types to known keys
- Reject access to keys not in the definition
- Prevent deletion of required keys

At runtime, `BookDict(...)` is equivalent to `dict(...)`. There are no instance attributes, no default values, and no method definitions.

## In Practice

`TypedDict` is most useful when you pass dicts through function boundaries and want the checker to verify key/value consistency:

```python
def to_xml(book: BookDict) -> str:
    elements = []
    for key, value in book.items():
        if isinstance(value, list):
            elements.extend(f"<AUTHOR>{n}</AUTHOR>" for n in value)
        else:
            tag = key.upper()
            elements.append(f"<{tag}>{value}</{tag}>")
    return "<BOOK>\n" + "\n".join(elements) + "\n</BOOK>"
```

The annotation `book: BookDict` tells the checker what keys and types to expect. But if the dict comes from `json.loads()`, the checker cannot verify the actual content -- `json.loads` returns `Any`.

For **runtime validation** of JSON-like data, use `pydantic.BaseModel` or `dataclasses` with manual validation. `TypedDict` is purely a static-analysis tool.

## Common Pitfalls

- **False sense of security**: Assigning `json.loads(data)` to a `BookDict` variable satisfies the checker, but the actual data could be anything. Mypy's `--disallow-any-expr` flag can help catch this.
- **Confusing it with data class builders**: Unlike `NamedTuple` or `@dataclass`, `TypedDict` does not create a custom class, does not support default values, and does not provide attribute access (`book.title` fails; use `book["title"]`).
- **No method definitions**: You cannot add methods to a `TypedDict` class.

## See Also

- [[runtime-type-hints]] -- how type hints are stored and accessed at runtime
- [[type-casting]] -- another static-only construct that has no runtime effect
