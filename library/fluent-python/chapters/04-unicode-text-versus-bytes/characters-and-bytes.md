---
title: Characters vs Bytes
aliases: [Characters and Bytes, str vs bytes, Code Points]
book: fluent-python
chapter: 4
concept: characters-and-bytes
tags: [unicode, str, bytes, code-points, encoding]
---

# Characters vs Bytes

## Core Idea

A **character** is an abstract identity -- a Unicode **code point** (a number from U+0000 to U+10FFFF). A **byte** is a concrete 8-bit value (0--255). The same character can map to completely different byte sequences depending on the **encoding** used.

Python 3 enforces a hard separation:
- `str` holds Unicode text (sequences of code points)
- `bytes` and `bytearray` hold raw binary data (sequences of integers 0--255)

## Key Details

### Code Points vs Byte Representations

The letter 'A' (U+0041) is always the same character, but:
- In UTF-8 it is the single byte `\x41`
- In UTF-16LE it is the two bytes `\x41\x00`

The Euro sign (U+20AC):
- UTF-8: three bytes `\xe2\x82\xac`
- UTF-16LE: two bytes `\xac\x20`

### bytes and bytearray Behavior

- Indexing a `bytes` object returns an **int** (not a character): `b'cafe'[0]` returns `99`
- Slicing returns a `bytes` object: `b'cafe'[:1]` returns `b'c'`
- `bytearray` is the mutable counterpart of `bytes`
- Both support most `str` methods except formatting and Unicode-specific ones

### Building bytes

```python
bytes('text', encoding='utf_8')     # from str + encoding
bytes([72, 101, 108])               # from iterable of ints
bytes.fromhex('31 4B CE A9')        # from hex string
bytes(array.array('h', [1, 2]))     # from buffer protocol
```

## Connections

- [[encoding-and-decoding]] -- how to convert between str and bytes
- [[text-file-handling]] -- the Unicode sandwich pattern for I/O
- [[unicode-database-and-dual-mode]] -- re and os behave differently with str vs bytes
