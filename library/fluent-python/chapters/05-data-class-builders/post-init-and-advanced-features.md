---
title: "Post-init Processing and Advanced Features"
slug: post-init-and-advanced-features
chapter: 5
book: "Fluent Python"
type: code-heavy
depends_on:
  - dataclass-decorator-and-fields
tags: [dataclass, __post_init__, ClassVar, InitVar, validation, computed-fields]
---

# Post-init Processing and Advanced Features

Beyond basic field declaration, `@dataclass` provides mechanisms for validation, computed fields, class-level attributes, and init-only parameters.

## `__post_init__`

The generated `__init__` calls `__post_init__` as its final step (if the method exists). Common uses:

1. **Validation** -- check field values and raise exceptions
2. **Computed fields** -- derive one field from others

```python
from dataclasses import dataclass, field

@dataclass
class ClubMember:
    name: str
    guests: list[str] = field(default_factory=list)

@dataclass
class HackerClubMember(ClubMember):
    all_handles: set = field(default_factory=set, init=False, repr=False)
    handle: str = ''

    def __post_init__(self):
        if self.handle == '':
            self.handle = self.name.split()[0]  # computed from name
        if self.handle in type(self).all_handles:
            raise ValueError(f"handle {self.handle!r} already exists.")
        type(self).all_handles.add(self.handle)
```

## `typing.ClassVar` -- Class-Level Attributes

In a `@dataclass`, every annotated attribute becomes an instance field by default. To declare a **class attribute** (shared across instances), wrap the type in `ClassVar`:

```python
from typing import ClassVar
from dataclasses import dataclass

@dataclass
class HackerClubMember:
    all_handles: ClassVar[set[str]] = set()  # class attribute, NOT a field
    name: str
    handle: str = ''
```

`@dataclass` ignores `ClassVar`-annotated attributes: they are not included in `__init__`, `__repr__`, or `__eq__`.

This is one of only two cases where `@dataclass` cares about the actual type in the annotation (the other is `InitVar`).

## `dataclasses.InitVar` -- Init-Only Parameters

Sometimes you need constructor arguments that are **not stored** as instance attributes. Declare them with `InitVar`:

```python
from dataclasses import dataclass, InitVar

@dataclass
class C:
    i: int
    j: int = None
    database: InitVar[dict] = None

    def __post_init__(self, database):
        if self.j is None and database is not None:
            self.j = database.lookup('j')
```

`InitVar` fields:
- Appear as `__init__` parameters
- Are passed to `__post_init__` as arguments (you must add them to the signature)
- Are **not** stored as instance attributes
- Are **not** listed by `dataclasses.fields()`

## Dublin Core Example

A realistic `@dataclass` using multiple features:

```python
from dataclasses import dataclass, field, fields
from typing import Optional
from enum import Enum, auto
from datetime import date

class ResourceType(Enum):
    BOOK = auto()
    EBOOK = auto()
    VIDEO = auto()

@dataclass
class Resource:
    """Media resource description."""
    identifier: str
    title: str = '<untitled>'
    creators: list[str] = field(default_factory=list)
    date: Optional[date] = None
    type: ResourceType = ResourceType.BOOK
    description: str = ''
    language: str = ''
    subjects: list[str] = field(default_factory=list)

    def __repr__(self):
        cls_name = self.__class__.__name__
        indent = ' ' * 4
        res = [f'{cls_name}(']
        for f in fields(self):
            value = getattr(self, f.name)
            res.append(f'{indent}{f.name} = {value!r},')
        res.append(')')
        return '\n'.join(res)
```

This pattern -- using `dataclasses.fields()` to iterate over field metadata -- is powerful for building custom `__repr__`, serializers, and validators.

## Inheritance Ordering

When a `@dataclass` inherits from another `@dataclass`, the fields of the parent come first in `__init__`. All fields without defaults must precede fields with defaults across the full hierarchy.

## See Also

- [[dataclass-decorator-and-fields]] -- basic decorator and field options
- [[data-class-as-code-smell]] -- when to add behavior to data classes
- [[type-hints-101]] -- how annotations drive field generation
