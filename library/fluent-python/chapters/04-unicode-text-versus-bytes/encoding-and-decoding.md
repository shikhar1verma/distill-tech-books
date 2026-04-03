---
title: Encoding and Decoding
aliases: [Codecs, UTF-8, Encode Decode, UnicodeError, BOM]
book: fluent-python
chapter: 4
concept: encoding-decoding
tags: [unicode, encoding, decoding, utf-8, latin-1, BOM, error-handling]
---

# Encoding and Decoding

## Core Idea

**Encoding** converts `str` (code points) to `bytes`. **Decoding** converts `bytes` back to `str`. The algorithm that performs this conversion is called a **codec**. Python ships with 100+ codecs; the dominant one on the web is **UTF-8** (used by 97% of websites).

Memory aid: **bytes** are cryptic machine dumps, so you **decode** them to get human-readable `str`. You **encode** human text to `bytes` for storage or transmission.

## Key Codecs

| Codec | Notes |
|-------|-------|
| `utf_8` | Variable-length (1--4 bytes), handles all Unicode, web standard |
| `latin_1` / `iso8859_1` | 1 byte per char, basis for cp1252 and Unicode itself |
| `cp1252` | Microsoft's latin_1 superset (curly quotes, Euro sign) |
| `ascii` | 7-bit, only 128 characters |
| `utf_16` | 2+ bytes per char, uses BOM for byte order |

## Error Handling

### UnicodeEncodeError (str -> bytes)

When a character has no mapping in the target encoding:

```python
city = 'Sao Paulo'
city.encode('cp437', errors='ignore')          # silently drops chars
city.encode('cp437', errors='replace')         # replaces with '?'
city.encode('cp437', errors='xmlcharrefreplace')  # XML entities
```

### UnicodeDecodeError (bytes -> str)

When a byte sequence is invalid for the assumed encoding:

```python
b'Montr\xe9al'.decode('utf_8')                # raises UnicodeDecodeError
b'Montr\xe9al'.decode('utf_8', errors='replace')  # uses U+FFFD
```

**Danger:** Legacy 8-bit codecs like `cp1252` and `koi8_r` decode *any* byte stream without error -- they silently produce garbage (mojibake).

### Detecting Encoding

You cannot reliably determine encoding from bytes alone. Use the **Chardet** library for heuristic detection. Leo's hack: try UTF-8 first; if it raises `UnicodeDecodeError`, fall back to `cp1252`.

## BOM (Byte Order Mark)

UTF-16 prepends `b'\xff\xfe'` (little-endian) or `b'\xfe\xff'` (big-endian) to indicate byte order. Use `utf_16le` or `utf_16be` to avoid BOM.

UTF-8 does not need a BOM, but Windows apps (Notepad, Excel) sometimes add one (`b'\xef\xbb\xbf'`). Use the `utf-8-sig` codec to handle this: it strips the BOM on read and adds it on write.

## Connections

- [[characters-and-bytes]] -- the fundamental str/bytes distinction
- [[text-file-handling]] -- always pass `encoding=` to `open()`
- [[unicode-normalization]] -- even after correct decoding, strings may need normalization
