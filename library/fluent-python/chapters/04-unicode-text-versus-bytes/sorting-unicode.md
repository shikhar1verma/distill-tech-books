---
title: Sorting Unicode Text
aliases: [Unicode Sorting, locale.strxfrm, pyuca, Unicode Collation Algorithm]
book: fluent-python
chapter: 4
concept: sorting-unicode
tags: [unicode, sorting, locale, collation, pyuca, UCA]
---

# Sorting Unicode Text

## Core Idea

Python's `sorted()` compares strings by **code point values**, not linguistic order. This produces wrong results for any text with accented characters. For example, 'a' (U+00E7, code point 231) sorts after all ASCII letters.

## The Problem

```python
fruits = ['caju', 'atemoia', 'caja', 'acai', 'acerola']
sorted(fruits)
# ['acerola', 'atemoia', 'acai', 'caju', 'caja']  -- WRONG
# Expected: ['acai', 'acerola', 'atemoia', 'caja', 'caju']
```

## Solution 1: locale.strxfrm

The standard library approach. Transforms strings into sort keys that respect the locale's collation rules.

```python
import locale
locale.setlocale(locale.LC_COLLATE, 'pt_BR.UTF-8')
sorted(fruits, key=locale.strxfrm)
# ['acai', 'acerola', 'atemoia', 'caja', 'caju']
```

**Caveats:**
- `setlocale` is a **global** setting -- not safe in libraries
- The locale must be **installed on the OS**
- Locale names vary across platforms
- **Does not work reliably on macOS** (works on Linux and Windows)

## Solution 2: pyuca (Recommended)

A pure-Python implementation of the Unicode Collation Algorithm (UCA). Portable across all platforms.

```python
import pyuca
coll = pyuca.Collator()
sorted(fruits, key=coll.sort_key)
# ['acai', 'acerola', 'atemoia', 'caja', 'caju']
```

- No locale setup needed
- Works identically on Linux, macOS, and Windows
- Does not account for language-specific rules (e.g., Swedish sorts A after Z)

## Solution 3: PyICU

For language-specific collation rules, use **PyICU** (Python bindings for ICU):
- Respects per-language sort order (German vs Swedish handling of umlauts)
- Handles Turkish dotted/dotless I correctly
- Requires compiled C extension (harder to install)

## Connections

- [[unicode-normalization]] -- normalization alone doesn't fix sort order
- [[case-folding-and-text-utils]] -- case folding is separate from collation
- [[unicode-database-and-dual-mode]] -- the Unicode database contains collation tables
