---
title: Text File Handling and Encoding Defaults
aliases: [Unicode Sandwich, Encoding Defaults, open encoding]
book: fluent-python
chapter: 4
concept: text-file-handling
tags: [unicode, file-io, encoding-defaults, unicode-sandwich, best-practices]
---

# Text File Handling and Encoding Defaults

## Core Idea

The **Unicode sandwich** is the best practice for text I/O:

1. **Decode** `bytes` to `str` as early as possible on input
2. Process text exclusively as **`str`** in your business logic
3. **Encode** `str` to `bytes` as late as possible on output

Python 3's `open()` does encoding/decoding automatically in text mode. But you **must** pass `encoding=` explicitly, because the default encoding varies by platform.

## The Encoding Default Trap

```python
# BUG: writes UTF-8 but reads with platform default
open('file.txt', 'w', encoding='utf_8').write('cafe')
open('file.txt').read()  # On Windows (cp1252): garbled!

# FIX: always specify encoding on both sides
open('file.txt', 'w', encoding='utf_8').write('cafe')
open('file.txt', 'r', encoding='utf_8').read()  # correct
```

### Platform Defaults

| Setting | Linux/macOS | Windows |
|---------|------------|---------|
| `locale.getpreferredencoding()` | UTF-8 | cp1252 (varies) |
| `sys.stdout.encoding` | utf-8 | utf-8 (since 3.6) |
| `sys.getdefaultencoding()` | utf-8 | utf-8 |
| `sys.getfilesystemencoding()` | utf-8 | utf-8 (since 3.6) |

The most important default is `locale.getpreferredencoding()` -- it controls `open()` and redirected stdout/stdin.

## Rules of Thumb

- **Always pass `encoding=`** when calling `open()` for text files
- Use `'rb'` / `'wb'` modes only for genuinely binary files (images, etc.)
- Don't open text files in binary mode to analyze encoding -- use Chardet instead
- On Windows, beware that stdout encoding changes when output is redirected to a file
- Use `'\N{UNICODE NAME}'` escapes in source code for clarity and safety

## Connections

- [[characters-and-bytes]] -- why the separation exists
- [[encoding-and-decoding]] -- codecs, error handlers, BOM
- [[unicode-normalization]] -- next step after correct decoding
