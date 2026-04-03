---
title: "Pattern Matching with Sequences"
book: "Fluent Python"
chapter: 2
tags: [pattern-matching, match-case, destructuring, sequences, python310]
related:
  - "[[sequence-unpacking]]"
  - "[[tuples-as-records-and-immutable-lists]]"
  - "[[slicing]]"
---

## Summary

Python 3.10 introduced `match/case` (PEP 634), which provides declarative destructuring -- a more powerful form of unpacking. Sequence patterns can match by structure and length, include type checks, bind variables, use guards (`if` clauses), and employ wildcards (`_`) and `*` for variable-length matching. The shape of the pattern mirrors the shape of the data.

## How It Works

### Basic Sequence Matching

A sequence pattern matches if: (1) the subject is a sequence, (2) it has the same number of items, and (3) each item matches:

```python
def handle_command(message):
    match message:
        case ['BEEPER', frequency, times]:
            return f"Beep {frequency}Hz x{times}"
        case ['NECK', angle]:
            return f"Rotate {angle} degrees"
        case ['LED', ident, red, green, blue]:
            return f"Set LED {ident} to RGB({red},{green},{blue})"
        case _:
            raise ValueError(f"Unknown: {message}")
```

Patterns try each `case` in order. `_` is the wildcard catch-all.

### Guards

An `if` clause after the pattern adds runtime conditions. The guard can reference variables bound by the pattern:

```python
match record:
    case [name, _, _, (lat, lon)] if lon <= 0:
        print(f"{name} is in the Western hemisphere")
```

### Type Checks

Syntax like `str(name)` in a pattern performs a type check (not a constructor call):

```python
case [str(name), _, _, (float(lat), float(lon))]:
    # name must be str; lat, lon must be float
```

### Variable-Length Matching

Use `*` to match remaining items:

```python
case [str(name), *_, (float(lat), float(lon))]:
    # any number of items between name and coordinate pair
```

`*_` discards the extras; `*rest` binds them to a list.

### The `as` Keyword

Bind a sub-pattern to a variable:

```python
case [name, _, _, (lat, lon) as coord]:
    # coord = (lat, lon) as the original tuple
```

### What Counts as a Sequence

Sequence patterns match `list`, `tuple`, `range`, `deque`, `array.array`, `memoryview`, and other virtual subclasses of `collections.abc.Sequence`. Notably, `str`, `bytes`, and `bytearray` are treated as **atomic** values (not sequences) to prevent unintended matches.

### Brackets vs Parentheses

In patterns, `[]` and `()` are interchangeable. The notation does not distinguish between list and tuple subjects.

## In Practice

- Pattern matching excels at **command dispatching** -- routing messages based on structure.
- It makes **interpreter/parser** code much cleaner (see the Norvig lis.py refactoring in the book).
- Use guards to add conditions without nesting `if` blocks inside `case` bodies.
- Always include a **catch-all** `case _:` to avoid silent failures.

## Common Pitfalls

1. **Forgetting the catch-all.** Without `case _:`, an unmatched subject silently does nothing.
2. **Confusing pattern syntax with constructors.** `float(lat)` in a pattern is a type check, not a conversion.
3. **Expecting `str` to match as a sequence.** `match "hello"` with `case ['h', *rest]:` will NOT match. Convert first: `match tuple("hello")`.
4. **Mutating subjects.** Patterns are matched at the time of the `match` statement; subsequent mutations do not affect the match.

## See Also

- [[sequence-unpacking]] -- the precursor to pattern matching destructuring
- [[tuples-as-records-and-immutable-lists]] -- the typical subjects of sequence patterns
- PEP 634 -- Structural Pattern Matching: Specification
- Chapter 5 covers pattern matching with mappings
- Chapter 6 covers pattern matching with class instances
