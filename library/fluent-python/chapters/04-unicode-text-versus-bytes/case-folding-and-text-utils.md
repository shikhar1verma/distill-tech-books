---
title: Case Folding and Text Utilities
aliases: [casefold, shave_marks, Diacritic Removal, Text Matching]
book: fluent-python
chapter: 4
concept: case-folding-and-text-utils
tags: [unicode, casefold, normalization, diacritics, text-matching]
---

# Case Folding and Text Utilities

## Core Idea

**Case folding** via `str.casefold()` is the correct way to do case-insensitive comparison. It goes beyond `str.lower()` by handling ~300 additional code points (e.g., sharp-s 'ss' becomes 'ss', micro sign becomes Greek mu).

Combined with NFC normalization, this gives you robust text matching for multilingual text.

## casefold() vs lower()

For pure ASCII text, they are identical. The differences appear with special characters:

```python
'ss'.casefold()   # -> 'ss'  (two characters!)
'u'.casefold()   # -> 'u' (GREEK SMALL LETTER MU, different code point)
'ss'.lower()      # -> 'ss'  (unchanged)
'u'.lower()      # -> 'u'  (unchanged)
```

## Utility Functions

### Safe Case-Sensitive Comparison

```python
from unicodedata import normalize

def nfc_equal(str1, str2):
    return normalize('NFC', str1) == normalize('NFC', str2)
```

### Safe Case-Insensitive Comparison

```python
def fold_equal(str1, str2):
    return (normalize('NFC', str1).casefold() ==
            normalize('NFC', str2).casefold())

fold_equal('Strasse', 'strasse')  # True
fold_equal('cafe', 'CAFE\u0301')  # True
```

## Removing Diacritics

Useful for search, URL generation, and ASCII-only contexts.

```python
import unicodedata

def shave_marks(txt):
    """Remove all diacritic marks."""
    norm_txt = unicodedata.normalize('NFD', txt)
    shaved = ''.join(c for c in norm_txt
                     if not unicodedata.combining(c))
    return unicodedata.normalize('NFC', shaved)

shave_marks('cafe')    # -> 'cafe'
shave_marks('acai')    # -> 'acai'
```

For Latin-only stripping (preserves Greek/Cyrillic accents), check base characters against `string.ascii_letters` before removing combining marks.

## The asciize Pipeline

For aggressive Western-text-to-ASCII conversion:

1. `dewinize()` -- replace CP1252 symbols (curly quotes, em dashes, etc.) with ASCII equivalents using `str.maketrans()`
2. `shave_marks_latin()` -- remove diacritics from Latin characters only
3. Replace `'ss'` with `'ss'`
4. Apply NFKC normalization

**Warning:** This changes meaning. Use only when you specifically need ASCII output (URLs, legacy systems).

## Connections

- [[unicode-normalization]] -- NFC/NFD are prerequisite steps
- [[sorting-unicode]] -- normalization + folding doesn't fix sort order
- [[characters-and-bytes]] -- all this operates on str, not bytes
