---
title: "Comparing B-Trees and LSM-Trees"
book: "Designing Data-Intensive Applications"
chapter: 4
sequence: 3
tags: [system-design, storage-engines, lsm-tree, b-tree, databases]
related:
  - "[[01-log-structured-storage-lsm-trees]]"
  - "[[02-b-trees-and-page-oriented-storage]]"
---

# Comparing B-Trees and LSM-Trees

> **One-sentence summary.** LSM-trees win on write throughput because they turn every mutation into a large sequential write, while B-trees usually win on read latency and predictability because one lookup touches only a handful of pages — but the real answer depends on your workload, and you should benchmark on a realistically aged dataset.

## How It Works

Both families solve the same problem — a durable, ordered key-value index on disk — but from opposite directions. A [[02-b-trees-and-page-oriented-storage]] mutates data **in place**: each write finds the right 4–8 KiB page, overwrites it, and logs the change in a WAL for crash recovery. A [[01-log-structured-storage-lsm-trees]] appends everything: writes land in an in-memory memtable, get flushed as an immutable SSTable, and are later reorganized by background compaction. In-place vs append-only is the single axis that drives every trade-off below.

That structural difference translates into an I/O pattern difference. B-trees issue many small, scattered writes — one per modified page — which looks like random I/O to the disk. LSM-trees issue fewer, much larger, sequential writes when flushing memtables and rewriting SSTables during compaction. On spinning disks the gap is dramatic (milliseconds of seek time per random write); on SSDs it is smaller but still real, because the flash translation layer erases 512 KiB blocks at a time and sequential workloads leave whole blocks cleanly reclaimable, while random workloads force the garbage collector to shuffle valid pages around before erasing.

## Read Performance

A B-tree read walks one page per level from root to leaf — typically 3–4 pages for a tree holding billions of keys. That path is short, fully cached for hot nodes, and its cost barely varies with dataset size, giving B-trees their signature **predictable read latency**.

An LSM read must consult the memtable plus every SSTable that might contain the key, newest to oldest, until a hit (or a tombstone) is found. Bloom filters make most of those per-SSTable probes skip disk I/O for keys that don't exist in that segment, which keeps point lookups competitive. **Range queries** are a different story: they can exploit SSTable sort order, but Bloom filters don't help (you'd need to hash every key in the range), so a range scan has to merge results from every level in parallel. B-trees, whose leaves are already in sorted order, handle ranges more cheaply.

## Write Amplification

Every engine turns one logical write into several physical ones. A B-tree writes the change to the WAL **and** to the tree page, and often re-writes the entire page even for a few-byte update, to guarantee crash consistency (torn-page protection). An LSM writes to the WAL, then again when the memtable flushes, then again at every compaction level the record passes through.

Which is worse depends on value size, key overwrite rate, and compaction strategy. For typical write-heavy workloads LSMs **tend to have lower write amplification** because they avoid full-page writes and can compress chunks of the SSTable. Lower write amp means more effective disk bandwidth for new writes — and less SSD wear.

## Trade-offs

| Aspect | B-Tree | LSM-Tree |
|---|---|---|
| Read latency | Predictable, ~3–4 page reads; one path per lookup | Variable; may probe many SSTables, Bloom filters mitigate point misses |
| Range scans | Cheap (sorted leaves) | More work (merge across levels, Bloom filters don't help) |
| Write latency | One WAL append + page(s) overwrite, often random I/O | One WAL append + memtable insert (in-memory); compaction deferred |
| Write amplification | WAL + page rewrite; full-page writes even for tiny changes | WAL + flush + every compaction level; often lower in practice |
| Sequential vs random writes | Random small page writes | Large sequential segment writes |
| Disk space | Fragmentation over time; needs vacuum/rebuild | Compresses well; size-tiered compaction temporarily ~2× during merges |
| Tombstones / deletion | Deleted immediately from tree | Delete is a tombstone; data lingers until compaction propagates it |
| Snapshots | Harder on in-place pages; CoW variants (LMDB) help | Easy — SSTables are immutable, just pin the set of files |
| Tail latency | Stable | Spikes from compaction stalls and memtable backpressure |

## Real-World Examples

- **B-tree engines**: PostgreSQL, MySQL's InnoDB, SQL Server, SQLite, Oracle — the entire lineage of classic relational databases. LMDB uses a copy-on-write B-tree for lock-free snapshots.
- **LSM engines**: RocksDB (embedded, used inside many systems), LevelDB, Apache Cassandra, Apache HBase, ScyllaDB, and time-series stores like InfluxDB. Write-heavy workloads and wide-column stores gravitate here.
- **Hybrids**: WiredTiger (the default MongoDB engine) supports both a B-tree and an LSM table type per collection. Many "SQL on LSM" engines (CockroachDB, TiDB, YugabyteDB) layer relational semantics on top of RocksDB — you get LSM write characteristics with a relational front end. See also [[04-secondary-and-clustered-indexes]] for how either engine can back a secondary index.

## Common Pitfalls

- **Benchmarking on an empty LSM.** A fresh LSM has no SSTables to compact, so every byte of disk bandwidth goes to new writes. Numbers look spectacular — and collapse once the dataset ages and compaction starts competing for I/O. Always benchmark past the point where the steady-state compaction backlog forms.
- **Assuming LSM is always faster for writes.** If your workload is update-heavy on a small hot key set, a B-tree may coalesce those updates into fewer page writes, while an LSM re-writes every version through every compaction level. Measure, don't assume.
- **Ignoring read amplification on deep LSMs.** Many compaction levels plus poor Bloom filter tuning means each point lookup probes many SSTables. For read-mostly workloads, a B-tree's bounded path length is hard to beat.
- **Forgetting tombstone propagation for compliance.** "Delete this user's data" on an LSM means writing a tombstone, not erasing bytes. The record persists on disk across every level it has reached until compaction finally rewrites that level. If you have GDPR/CCPA obligations with strict deadlines, verify your engine's deletion latency — or choose one that can force-propagate tombstones.
- **Overlooking tail latency from backpressure.** When writes outrun compaction, engines like RocksDB stall or throttle client writes until the memtable drains. A p50 write latency of 1 ms can hide a p99.9 of several seconds. Capacity-plan for sustained write rate, not peak.

## See Also

- [[01-log-structured-storage-lsm-trees]] — the LSM family in depth: memtable, SSTables, compaction, Bloom filters
- [[02-b-trees-and-page-oriented-storage]] — the page-oriented alternative and its WAL/CoW crash-consistency story
- [[04-secondary-and-clustered-indexes]] — both engines can underpin secondary indexes; the choice affects write cost and snapshot behavior there too
