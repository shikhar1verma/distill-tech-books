---
title: The Unicode Database and Dual-Mode APIs
aliases: [unicodedata, Character Finder, Dual-Mode APIs, str vs bytes in re and os]
book: fluent-python
chapter: 4
concept: unicode-database-and-dual-mode
tags: [unicode, unicodedata, regex, os, dual-mode, character-metadata]
---

# The Unicode Database and Dual-Mode APIs

## Core Idea

The Unicode standard includes a full **database** of character metadata: names, categories, numeric values, and more. Python's `unicodedata` module exposes this data. Additionally, key standard library modules (`re`, `os`) are **dual-mode**: they accept both `str` and `bytes` arguments but behave differently for each type.

## The unicodedata Module

### Key Functions

| Function | Returns | Example |
|----------|---------|---------|
| `name(char)` | Official Unicode name | `name('A')` -> `'LATIN CAPITAL LETTER A'` |
| `category(char)` | Two-letter category code | `category('A')` -> `'Lu'` (Letter, uppercase) |
| `numeric(char)` | Numeric value as float | `numeric('1/2')` -> `0.5` |
| `normalize(form, str)` | Normalized string | See [[unicode-normalization]] |
| `combining(char)` | Combining class (0 = not combining) | Used in diacritic removal |

### Character Categories

The two-letter codes follow a pattern: first letter = major class, second = subclass.

- **L** = Letter (Lu=upper, Ll=lower, Lt=titlecase, Lm=modifier, Lo=other)
- **N** = Number (Nd=decimal, Nl=letter-number, No=other)
- **S** = Symbol, **P** = Punctuation, **Z** = Separator, **C** = Control/Other

### Building a Character Finder

```python
import unicodedata, sys

def find(*query_words, start=32, end=sys.maxunicode + 1):
    query = {w.upper() for w in query_words}
    for code in range(start, end):
        char = chr(code)
        name = unicodedata.name(char, None)
        if name and query.issubset(name.split()):
            print(f'U+{code:04X}\t{char}\t{name}')
```

Uses `set.issubset()` to check if all query words appear in the character name -- an elegant pattern that avoids nested loops.

### Numeric Characters

Three levels of "numericness":

| Method | What it matches | Example chars |
|--------|----------------|---------------|
| `str.isdecimal()` | Decimal digits (0-9 in any script) | 1, &#x0969; |
| `str.isdigit()` | Digits + superscripts/subscripts | 1, &#x0969;, &#x00b2; |
| `str.isnumeric()` | Any numeric character | 1, &#x0969;, &#x00b2;, &#x00bc;, &#x2466; |

## Dual-Mode APIs

### re (Regular Expressions)

| Pattern type | `\d` matches | `\w` matches |
|-------------|-------------|-------------|
| `str` (e.g., `r'\d+'`) | All Unicode digits (Tamil, Arabic, etc.) | All Unicode letters + digits |
| `bytes` (e.g., `rb'\d+'`) | Only ASCII digits (0-9) | Only ASCII letters + digits + underscore |

Use the `re.ASCII` flag to force ASCII-only matching on `str` patterns.

### os (Filesystem)

| Argument type | Return type | Encoding |
|---------------|-------------|----------|
| `str` | `str` | Auto-encoded/decoded via `sys.getfilesystemencoding()` |
| `bytes` | `bytes` | Passed raw to OS -- can handle any filename |

Use `bytes` arguments when dealing with filenames that contain invalid Unicode sequences (common on Linux file servers with mixed-encoding clients).

Helper functions: `os.fsencode()` and `os.fsdecode()` convert between `str` and `bytes` filenames.

## Connections

- [[characters-and-bytes]] -- the fundamental distinction that drives dual-mode behavior
- [[encoding-and-decoding]] -- os functions use filesystem encoding internally
- [[unicode-normalization]] -- normalize before searching character names
