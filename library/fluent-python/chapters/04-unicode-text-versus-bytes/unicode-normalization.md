---
title: Unicode Normalization (NFC/NFD/NFKC/NFKD)
aliases: [NFC, NFD, NFKC, NFKD, Canonical Equivalence, Combining Characters]
book: fluent-python
chapter: 4
concept: unicode-normalization
tags: [unicode, normalization, NFC, NFD, NFKC, NFKD, combining-characters]
---

# Unicode Normalization

## Core Idea

The same visible character can have **multiple code point representations**. For example, 'e' (U+00E9) and 'e' + combining acute accent (U+0065 U+0301) look identical but are different sequences. Python considers them **not equal** unless you **normalize** first.

`unicodedata.normalize(form, text)` converts text to a standard form so equivalent strings compare as equal.

## The Four Normalization Forms

| Form | Action | Length | Use Case |
|------|--------|--------|----------|
| **NFC** | Compose to shortest | Shorter | Default for storage and comparison. W3C recommended. |
| **NFD** | Decompose to base + marks | Longer | Processing that needs to inspect combining marks. |
| **NFKC** | Compatibility compose | Varies | Search and indexing. **Lossy** -- changes meaning! |
| **NFKD** | Compatibility decompose | Varies | Search and indexing. **Lossy** -- changes meaning! |

## NFC and NFD (Safe)

```python
from unicodedata import normalize

s1 = 'cafe'            # e-acute as single code point
s2 = 'cafe\u0301'       # e + combining acute accent
s1 == s2                 # False
normalize('NFC', s1) == normalize('NFC', s2)   # True
normalize('NFD', s1) == normalize('NFD', s2)   # True
```

NFC is the preferred form:
- Keyboard drivers produce composed characters (NFC) by default
- W3C recommends NFC for web content
- NFC normalizes some single characters (e.g., OHM SIGN -> GREEK CAPITAL LETTER OMEGA)

## NFKC and NFKD (Lossy -- Use with Caution)

These replace **compatibility characters** with their preferred equivalents:

| Original | NFKC | Problem? |
|----------|------|----------|
| `'1/2'` | `'1/2'` (with fraction slash) | Subtle character change |
| `'4^2'` | `'42'` | **Meaning changed!** |
| `'u' (MICRO SIGN)` | `'u' (GREEK SMALL LETTER MU)` | Acceptable |

**Rule:** Use NFKC/NFKD only for search indexes or intermediate representations. Never for permanent storage.

## Connections

- [[case-folding-and-text-utils]] -- combine normalization with casefold() for robust matching
- [[encoding-and-decoding]] -- normalization comes after correct decoding
- [[sorting-unicode]] -- normalization alone doesn't fix sort order
