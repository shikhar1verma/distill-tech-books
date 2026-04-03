---
title: "Pattern Matching with Mappings"
chapter: 3
book: fluent-python
type: concept
slug: pattern-matching-mappings
tags: [pattern-matching, match-case, dict, python3.10, destructuring]
depends_on:
  - dict-comprehensions-unpacking-merging
---

# Pattern Matching with Mappings

## Overview

Python 3.10's `match/case` statement can destructure mapping objects. Mapping patterns look like dict literals and match any instance of `collections.abc.Mapping` (including `dict`, `OrderedDict`, `defaultdict`, etc.).

## Key Behavior: Partial Matching

Unlike sequence patterns, mapping patterns succeed on **partial** matches. Extra keys in the subject are silently ignored:

```python
record = {'type': 'book', 'title': 'Fluent Python', 'api': 2, 'authors': ['Ramalho']}
match record:
    case {'type': 'book', 'api': 2, 'authors': [*names]}:
        print(names)  # ['Ramalho'] -- 'title' key was ignored
```

## Capturing Extra Keys

Prefix a variable with `**` at the end of the pattern to capture unmatched key-value pairs as a dict. (`**_` is forbidden because it would be redundant.)

```python
food = {'category': 'ice cream', 'flavor': 'vanilla', 'cost': 199}
match food:
    case {'category': 'ice cream', **details}:
        print(details)  # {'flavor': 'vanilla', 'cost': 199}
```

## Practical Example: Semi-Structured Records

Pattern matching excels at handling semi-structured data (JSON APIs, document databases):

```python
def get_creators(record: dict) -> list:
    match record:
        case {'type': 'book', 'api': 2, 'authors': [*names]}:
            return names
        case {'type': 'book', 'api': 1, 'author': name}:
            return [name]
        case {'type': 'book'}:
            raise ValueError(f"Invalid 'book' record: {record!r}")
        case {'type': 'movie', 'director': name}:
            return [name]
        case _:
            raise ValueError(f'Invalid record: {record!r}')
```

## Important Details

- Key order in patterns is irrelevant (even for `OrderedDict` subjects).
- Pattern matching uses `d.get(key, sentinel)` internally, so `defaultdict`'s `default_factory` is **not** triggered.
- Patterns can be nested: mapping patterns inside sequence patterns and vice versa.

## Best Practices

1. Include a **type discriminator** field (e.g., `'type': 'book'`) to route records.
2. Include a **schema version** field (e.g., `'api': 2`) for forward compatibility.
3. Add catch-all `case` clauses for invalid records of known types **and** for completely unknown subjects.

## See Also

- [[dict-comprehensions-unpacking-merging]] -- building dicts
- [[defaultdict-and-missing]] -- why default_factory is not triggered during matching
