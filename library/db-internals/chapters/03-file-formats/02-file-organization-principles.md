---
title: "File Organization: Headers, Pages, and Fixed Schemas"
book: "Database Internals"
chapter: 3
sequence: 2
tags: [system-design, storage, file-formats, databases]
related:
  - "[[01-binary-encoding-primitives]]"
  - "[[03-slotted-pages]]"
  - "[[06-file-format-versioning]]"
---

# File Organization: Headers, Pages, and Fixed Schemas

> **One-sentence summary.** A database file is a fixed-size header followed by an array of equal-sized pages (optionally capped by a trailer), where each record separates fixed-size fields from variable-size fields using offset/length pairs so any field can be located in constant time.

## How It Works

On-disk files are designed the way C programmers hand-manage memory: you allocate a contiguous block and carve it up with fixed-size primitives and pointers. Unlike RAM, the OS will not transparently relocate, defragment, or garbage-collect your data — every byte must have an owner you can recover after a crash. The universal solution is a three-part layout. A **header** at offset 0 holds the format's magic number, version, page size, checksum algorithm, and usually a lookup table pointing at the start offsets of later sections. The bulk of the file is a sequence of **pages** — fixed-size slabs, typically 4–16 KB, chosen to be a multiple of the filesystem block so a single `pread` never straddles a device sector. A **trailer** at the end is optional and holds data that is only known after writes complete (e.g., an index or footer of record counts in immutable SSTables).

```mermaid
graph LR
  H[Header<br/>magic + version<br/>lookup table] --> P0[Page 0]
  P0 --> P1[Page 1]
  P1 --> Pn[... Page N]
  Pn --> T[Trailer<br/>optional footer]
```

Within a page, records themselves are built hierarchically: primitives compose into fields, fields into cells, cells into pages. For a fixed-schema record — say an employee row with `id`, `tax_number`, `date_of_birth`, `gender`, `first_name`, `last_name` — the trick is to **group fixed-size fields at the head** and push variable-size data into a tail. Since the fixed part has a known byte width, offsets to each fixed field are compile-time constants. For the variable tail you have two choices: pack the variable fields sequentially (compact, but reading `last_name` forces you to first read `first_name_length`), or store explicit `(offset, length)` pairs in the fixed header (costs extra bytes, but every variable field becomes O(1) to reach). Multi-part files usually also keep a **lookup table** in the header or trailer pointing at the start of each part, so a reader can jump straight to the section it needs without scanning.

## When to Use

- **On-disk B-Tree files.** The file header stores the root page ID and page size; every B-Tree node is exactly one page, so a page ID multiplied by page size gives the byte offset — no scanning, no indirection.
- **WAL and journal segments.** Write-ahead logs pre-allocate fixed-size segment files and append page-aligned records so recovery can scan forward block by block and tolerate a torn final page.
- **SSTable-style immutable files.** LSM engines write data pages first, then append an index block and footer (trailer) once sizes are known, letting readers `mmap` the file and seek directly to the footer to discover the index.

## Trade-offs

| Aspect | Advantage | Disadvantage |
|--------|-----------|--------------|
| Packed variable-size tail (no offsets) | Minimal bytes; no per-field overhead | O(k) to reach the k-th variable field; any field read scans predecessors |
| Explicit offset/length pairs in header | O(1) random access to any field; skip over values you don't need | Extra 2–4 bytes per variable field; header grows with schema |
| Fixed-size pages | Page ID ↔ byte offset is arithmetic; easy buffer-pool slot reuse; crash boundaries align with OS blocks | Internal fragmentation when records don't pack evenly; records larger than a page need overflow chains |
| Variable-size segments | No wasted tail space; one allocation per logical record | Complex free-space tracking; external fragmentation; pointer stability is harder |
| Header lookup table | Readers find sections without scanning | Header must be updated atomically on every section rewrite |

## Real-World Examples

- **PostgreSQL** uses 8 KB pages with a page header, an array of item (line) pointers growing from the low end, and tuple data growing from the high end — a slotted page built on exactly this fixed-header-plus-pages model.
- **SQLite** ships a 100-byte database header at offset 0 (magic string `"SQLite format 3\0"`, page size, file format version), then the entire file is a pure array of pages of that size.
- **Cassandra SSTables** use a family of files per table where a data file's footer points back to an index block, and versioning travels in the filename prefix (`na-*`, `ma-*`) rather than inside the header.
- **Protocol Buffers / FlatBuffers** contrast usefully: they are schema-driven binary formats with variable-length encodings and offset tables, but they are not page-based — they target message-level serialization rather than random-access on-disk storage.

## Common Pitfalls

- **Assuming C `struct` layout matches disk layout.** Compilers insert padding for alignment, and padding bytes vary by architecture. Always serialize fields explicitly (or use `#pragma pack`) instead of memcpy-ing a struct to disk.
- **Page size that does not match the filesystem block.** If your 8 KB page spans two 4 KB filesystem blocks, a power failure mid-write can tear the page — the classic motivation for PostgreSQL's `full_page_writes`.
- **Forgetting to version the header.** Without a version byte (or magic number) in a stable location, you cannot evolve the format without breaking old readers — upgrading means a full rewrite. See [[06-file-format-versioning]].
- **Ignoring endianness.** Writing integers in host byte order works until someone reads the file on a different CPU. Pick big-endian or little-endian up front and document it in the header.
- **Skipping the lookup table.** Without it, opening a multi-section file forces a linear scan to find the index or trailer, turning an O(1) seek into O(file size).

## See Also

- [[01-binary-encoding-primitives]] — the byte-level encoding of the fields that fill these pages
- [[03-slotted-pages]] — how a single page is organized internally once variable-size records are involved
- [[06-file-format-versioning]] — where to put the version number so the header itself can evolve
