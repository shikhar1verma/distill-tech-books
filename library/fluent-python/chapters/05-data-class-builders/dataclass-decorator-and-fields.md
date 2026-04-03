---
title: "@dataclass Decorator and Field Options"
slug: dataclass-decorator-and-fields
chapter: 5
book: "Fluent Python"
type: code-heavy
depends_on:
  - type-hints-101
tags: [dataclass, decorator, field, frozen, order, default_factory, mutable-defaults]
---

# `@dataclass` Decorator and Field Options

The `@dataclass` decorator from the `dataclasses` module is the most powerful and flexible of the three data class builders. It modifies the class in place via a class decorator (no inheritance or metaclass needed).

## Decorator Signature

```python
@dataclass(*, init=True, repr=True, eq=True, order=False,
           unsafe_hash=False, frozen=False)
```

| Option | Meaning | Default |
|---|---|---|
| `init` | Generate `__init__` | `True` |
| `repr` | Generate `__repr__` | `True` |
| `eq` | Generate `__eq__` | `True` |
| `order` | Generate `__lt__`, `__le__`, `__gt__`, `__ge__` | `False` |
| `unsafe_hash` | Generate `__hash__` (use with caution) | `False` |
| `frozen` | Make instances "immutable" | `False` |

The most useful non-default settings:
- **`frozen=True`** -- prevents accidental mutation; when combined with `eq=True`, also enables `__hash__`
- **`order=True`** -- enables comparison operators for sorting

## The `field()` Function

For per-field customization, use `dataclasses.field()`:

```python
from dataclasses import dataclass, field

@dataclass
class ClubMember:
    name: str
    guests: list[str] = field(default_factory=list)
    athlete: bool = field(default=False, repr=False)
```

| `field()` Option | Meaning | Default |
|---|---|---|
| `default` | Default value | `_MISSING_TYPE` |
| `default_factory` | Zero-arg callable producing default | `_MISSING_TYPE` |
| `init` | Include in `__init__` parameters | `True` |
| `repr` | Include in `__repr__` | `True` |
| `compare` | Use in `__eq__` and ordering methods | `True` |
| `hash` | Include in `__hash__` (`None` = use `compare` setting) | `None` |
| `metadata` | User-defined mapping, ignored by `@dataclass` | `None` |

## Mutable Default Values

`@dataclass` rejects mutable defaults (`list`, `dict`, `set`) to prevent the classic shared-mutable-default bug:

```python
@dataclass
class Bad:
    guests: list = []  # ValueError: mutable default is not allowed
```

Fix with `default_factory`:

```python
@dataclass
class Good:
    guests: list = field(default_factory=list)  # each instance gets its own list
```

Note: only `list`, `dict`, and `set` are caught. Other mutable types (e.g., custom classes) are not detected -- you must remember to use `default_factory` yourself.

## Frozen Data Classes and Hashing

When `frozen=True`:
- `__setattr__` and `__delattr__` are generated to raise `FrozenInstanceError`
- If `eq=True` (the default), `__hash__` is also generated using all fields with `compare=True`
- Instances become usable as dict keys and set members

```python
@dataclass(frozen=True)
class Coordinate:
    lat: float
    lon: float

c = Coordinate(55.76, 37.62)
hash(c)          # works
{c: 'Moscow'}   # works as dict key
c.lat = 0       # FrozenInstanceError
```

## Introspection with `fields()`, `asdict()`, `replace()`

```python
from dataclasses import fields, asdict, replace

for f in fields(some_instance):
    print(f.name, f.default, f.type)

d = asdict(some_instance)           # recursive dict conversion
new = replace(some_instance, lat=0) # new instance with one field changed
```

## See Also

- [[post-init-and-advanced-features]] -- `__post_init__`, `ClassVar`, `InitVar`
- [[data-class-as-code-smell]] -- when too many data classes indicate a design problem
- [[data-class-builders-overview]] -- comparison of all three builders
