---
title: "Pattern Matching Class Instances"
slug: pattern-matching-class-instances
chapter: 5
book: "Fluent Python"
type: code-heavy
depends_on:
  - data-class-builders-overview
tags: [pattern-matching, match-case, __match_args__, structural-pattern-matching, Python-3.10]
---

# Pattern Matching Class Instances

Python 3.10's `match`/`case` supports class patterns for matching arbitrary class instances by type and attributes -- not just sequences and mappings. Data class builders automatically generate `__match_args__`, enabling positional patterns.

## Three Variations of Class Patterns

### 1. Simple Class Patterns

For the nine "blessed" built-in types (`bytes`, `dict`, `float`, `frozenset`, `int`, `list`, `set`, `str`, `tuple`), the argument captures the whole subject:

```python
match x:
    case float(n):
        print(f"a float: {n}")
    case int(n):
        print(f"an int: {n}")
```

**Gotcha:** `case float:` (without parentheses) matches *anything* and binds it to a variable named `float`. Always use `case float():` with parentheses.

### 2. Keyword Class Patterns

Match by attribute name -- works with any class that has public instance attributes:

```python
from typing import NamedTuple

class City(NamedTuple):
    continent: str
    name: str
    country: str

match city:
    case City(continent='Asia'):
        results.append(city)
    case City(continent='Asia', country=cc):
        results.append(cc)  # cc bound to country value
```

Keyword patterns are readable and explicit. The pattern variable can even share the attribute name: `country=country`.

### 3. Positional Class Patterns

Match by position in `__match_args__` -- more concise but requires the class to define this attribute:

```python
match city:
    case City('Asia'):           # first arg matches continent
        results.append(city)
    case City('Asia', _, country):  # positional: continent, name, country
        results.append(country)
```

## `__match_args__`

This special class attribute maps positional pattern arguments to attribute names:

```python
City.__match_args__  # ('continent', 'name', 'country')
```

All three data class builders generate `__match_args__` automatically:
- `collections.namedtuple`: from field names
- `typing.NamedTuple`: from field names
- `@dataclass`: from field names

For custom classes without a builder, you must define `__match_args__` yourself.

## Combining Keyword and Positional

You can mix positional and keyword arguments in a pattern. This is useful when `__match_args__` lists only some attributes:

```python
match city:
    case City('Asia', name=n):  # positional for continent, keyword for name
        print(n)
```

## Patterns for Non-Data Classes

Class patterns work with *any* class instance, not just data classes. For classes without `__match_args__`, use keyword patterns:

```python
class RegularClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

obj = RegularClass(1, 2)
match obj:
    case RegularClass(x=1, y=y_val):
        print(f"y is {y_val}")
```

## See Also

- [[data-class-builders-overview]] -- how the three builders generate `__match_args__`
- [[typed-named-tuples]] -- NamedTuple used in the City example
- [[classic-named-tuples]] -- namedtuple also supports positional matching
