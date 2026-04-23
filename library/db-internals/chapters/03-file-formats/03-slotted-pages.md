---
title: "Slotted Pages for Variable-Size Records"
book: "Database Internals"
chapter: 3
sequence: 3
tags: [system-design, storage, page-layout, databases, b-tree]
related:
  - "[[02-file-organization-principles]]"
  - "[[04-cell-layout]]"
  - "[[05-managing-free-space]]"
---

# Slotted Pages for Variable-Size Records

> **One-sentence summary.** A slotted page stores variable-size records by splitting each page into a header, a pointer array growing inward from one end, and a cell region growing inward from the other — so records keep their insertion-order bytes on disk while the sorted pointer array preserves logical key order.

## The Problem

Concatenating records inside a page as `(key, value, pointer)` triplets breaks in three ways.

First, **variable-size records do not align into freed holes**. Delete a 40-byte record and later insert a 70-byte one and the gap is useless; insert a 10-byte one and you have a new 30-byte fragment no one can reuse. Without bookkeeping you either shift the tail of the page on every delete (O(n) per operation) or accept ever-growing dead space.

Second, **you cannot reference a cell stably**. If callers remember "row X lives at byte offset 1280," any compaction that moves cells invalidates every outstanding reference — B-Tree internal nodes, secondary indexes, undo logs, cursors. Storage engines depend on moving records without telling the rest of the world.

Third, the obvious escape — **fixed-size segments** — wastes space for short records and still cannot fit records larger than the segment. Slotted pages solve all three.

## How It Works

A slotted page upholds three invariants:

1. **Minimal overhead.** The only metadata beyond the records themselves is a small array of offsets — the slot directory.
2. **Space is reclaimed by defragmenting.** Deletes nullify a pointer; compaction is deferred until the page needs space it does not have.
3. **Cells are referenced by slot ID, not by physical offset.** Slot IDs are stable; offsets behind them can change freely when the page is rewritten.

The page has the header at the top, cell pointers growing rightward from just after the header, and cells growing leftward from the end of the page. Free space is whatever sits between the two advancing fronts; the page is full only when they collide.

```mermaid
graph LR
  H[Header] --- P["Pointer Array ->> growing right"]
  P --- F[(Free Space)]
  F --- C["<<- Cells growing left"]
```

### The Tom / Leslie / Ron example

Start with an empty page and insert three names in order: **Tom**, **Leslie**, **Ron**.

- Append `Tom` at the high end of the page. Write pointer `p0 -> offset(Tom)` at the low end.
- Append `Leslie` to the left of `Tom`. Cells on disk are physically `[Leslie][Tom]` (insertion order), but the pointer array is re-sorted so that slot 0 points to `Leslie` and slot 1 points to `Tom`.
- Insert `Ron`. The cell is appended to the left of `Leslie`, so on-disk order is `[Ron][Leslie][Tom]`. The pointer array must reflect `Leslie, Ron, Tom` alphabetically, so existing pointers shift rightward from the insertion point to make room for a new pointer to `Ron`.

Two orderings now coexist on one page. **Cells on disk stay in insertion order** — no shifting of cell bytes on write. **Pointers stay in key order** — so a reader does binary search on the pointer array in O(log n), dereferences through the slot, and lands on the cell wherever it lives. Deletion becomes trivial: nullify the pointer, leave the bytes alone, and reclaim space on the next defragmentation.

## When to Use

- **Variable-size records** — strings, BLOBs, JSON, anything that does not compress to a uniform record width.
- **Leaf nodes of B-Trees** — where variable-size keys and values live and where external references (internal nodes, secondary indexes) must keep pointing at the same logical record after page rewrites.
- **Any page that needs stable external identity under relocation** — the slot ID survives defragmentation; the byte offset does not.

## Trade-offs

| Aspect | Advantage | Disadvantage |
|---|---|---|
| Pointer indirection | Cells relocatable without invalidating references | One extra dereference per read vs in-place layout |
| Defragmentation | Deletes are O(1); compaction is amortized | Compaction pass is O(n) and may stall a write |
| Mark-and-reuse | Reclaims arbitrarily sized holes via freeblocks | Fragmentation accumulates until compaction |
| Sorted offsets | Binary search over keys inside a page | Insert is O(n) on the pointer array (shift tail) |

## Real-World Examples

- **PostgreSQL** — heap pages use exactly this layout. The slot directory is the `ItemIdData` array (aka *line pointers*); TIDs are `(page number, slot index)` pairs, and `VACUUM` is the defragmentation pass. Stable line pointers let indexes reference a tuple that later gets compacted within its page.
- **SQLite** — pages carry a pointer array and cell region with the same two-way growth. Deleted cells become *freeblocks* tracked in a linked list, rebuilt on defragmentation.
- **InnoDB** — a variation with the *compact* row format: a page directory of "slots" points into groups of records linked by next-record offsets — same decoupling of logical and physical order, tuned for clustered-index storage.
- **LSM SSTables (contrast)** — immutable by design. Written once and never updated, they skip slotted-page machinery entirely and use a dense sorted layout plus a sparse index. Slotted pages solve mutation; SSTables avoid it.

## Common Pitfalls

- **Conflating slot IDs with offsets.** External references (TIDs, rowids, B-Tree child pointers) must be slot IDs. If they become raw byte offsets, you cannot defragment without rewriting every index.
- **Forgetting to re-sort the pointer array on insert.** If you just append both the cell and the pointer, binary search silently returns wrong answers. Find the key position and shift tail pointers.
- **Not updating pointer metadata during defragmentation.** Compaction moves cells; every slot entry that referenced a moved cell must be rewritten to the new offset in the same atomic step. Skipping one slot corrupts the page.
- **Treating "bytes free" as "insertable."** Total free space and the largest contiguous free region differ on a fragmented page — a 500-byte cell may not fit into 600 bytes spread across five freeblocks.

## See Also

- [[02-file-organization-principles]] — pages, headers, and fixed-schema records that slotted pages sit inside.
- [[04-cell-layout]] — what actually lives inside a slot: key cells vs key-value cells.
- [[05-managing-free-space]] — freeblocks, first-fit / best-fit, and when defragmentation kicks in.
