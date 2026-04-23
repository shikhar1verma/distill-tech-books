---
title: "Isolation Levels and Read/Write Anomalies"
book: "Database Internals"
chapter: 5
sequence: 5
tags: [system-design, databases, transactions, concurrency]
related:
  - "[[06-concurrency-control-strategies]]"
  - "[[07-locks-latches-and-btree-concurrency]]"
---

# Isolation Levels and Read/Write Anomalies

> **One-sentence summary.** Isolation levels are a ladder of precise promises about which concurrent-execution anomalies a transaction will and won't observe, with *serializable* at the top — meaning the result must be equivalent to *some* serial order of the transactions, though not necessarily the real-time order.

## How It Works

The gold standard for correctness under concurrency is **serializability**. A *schedule* (an interleaving of operations from multiple transactions) is serializable if it produces the same result as *some* complete serial execution of the same transactions — any order will do, as long as there exists one. This is the "I" in ACID: isolation, formally, means that a concurrent schedule is indistinguishable from running the transactions one at a time.

Serializability is easy to confuse with **linearizability**, but they differ. Linearizability requires operations to appear in the real-time order in which they occurred — once T1 commits, every later transaction must see its effect. Serializability only requires that *some* serial order exists; a serializable database may order two non-overlapping commits as `T2 then T1` as long as no client can tell. Systems that give you both are *strict* (or externally consistent) serializable — Spanner is the famous example.

Weaker levels permit specific anomalies. The SQL standard names three **read anomalies** and engineers have since added three **write anomalies**:

- **Dirty read** — T2 reads a row T1 has written but not yet committed. If T1 aborts, T2 has seen a value that never existed.
- **Nonrepeatable read (fuzzy read)** — T1 reads a row, T2 modifies and commits it, then T1 reads the same row again and gets a different value within the same transaction.
- **Phantom read** — T1 runs the same range query twice (`WHERE age > 30`) and the second result set contains or is missing rows because some other transaction inserted/deleted matching rows and committed in between.
- **Lost update** — T1 and T2 both read `V`, each computes a new value, and both write back. Whichever commits second silently clobbers the other's update.
- **Dirty write** — T2 overwrites a value that T1 wrote but hasn't yet committed. Makes rollback incoherent, because what would "undo T1" even mean if T2 has already built on it?
- **Write skew** — T1 and T2 each read overlapping state, each individually preserves an invariant, but their *combined* effect violates it. Canonical example: two on-call doctors each check the roster, see the other is still on-call, and both mark themselves off — leaving zero on-call.

The SQL isolation ladder is defined by which anomalies each rung forbids:

| Isolation Level   | Dirty Read | Nonrepeatable Read | Phantom Read | Lost Update | Write Skew |
|-------------------|:----------:|:------------------:|:------------:|:-----------:|:----------:|
| Read Uncommitted  | allowed    | allowed            | allowed      | allowed     | allowed    |
| Read Committed    | prevented  | allowed            | allowed      | allowed     | allowed    |
| Repeatable Read   | prevented  | prevented          | allowed\*    | allowed\*   | allowed    |
| Snapshot Isolation| prevented  | prevented          | prevented    | prevented   | allowed    |
| Serializable      | prevented  | prevented          | prevented    | prevented   | prevented  |

\* by the SQL standard; specific engines differ (see MySQL below).

**Snapshot isolation (SI)** deserves its own row. A transaction reads from a consistent snapshot of the database as of its start time; it commits only if no concurrent committed transaction modified any key in its write set. This precludes lost update automatically — the second writer is aborted. But SI **does not prevent write skew**: if T1 and T2 write *different* keys based on overlapping reads, neither write-set conflicts, both commit, and the invariant silently breaks. For years, PostgreSQL shipped what it called "SERIALIZABLE" that was in fact snapshot isolation; true serializability arrived with **Serializable Snapshot Isolation (SSI)** in 9.1, which tracks rw-dependencies and aborts transactions forming a dangerous cycle.

## When to Use

- **Default to Read Committed for general OLTP.** Most web apps don't need stronger — each HTTP request maps to a short transaction, and occasional nonrepeatable reads within a request are either harmless or guarded by application-level versioning (optimistic UI, `IF MATCH` headers).
- **Snapshot Isolation for reporting and long reads.** Analytics queries that scan millions of rows need a stable view without blocking writers; SI gives it for free without taking locks.
- **Serializable for invariant-critical work.** Money transfers, inventory decrements, scheduling on-call rotations, uniqueness constraints you can't express in SQL. Whenever a correctness argument uses the word "and" — *"the total must stay positive **and** both accounts exist"* — you likely need serializable.

## Trade-offs

| Isolation Level    | Throughput         | Anomalies allowed           | Coordination cost                                   |
|--------------------|--------------------|-----------------------------|------------------------------------------------------|
| Read Uncommitted   | highest            | all                         | none — readers just read the latest bytes            |
| Read Committed     | very high          | nonrepeatable, phantom, skew| short read locks or per-statement snapshots          |
| Repeatable Read    | high               | phantom (standard), skew    | long read locks or single transaction-level snapshot |
| Snapshot Isolation | high (MVCC-based)  | write skew                  | version storage + write-set conflict check at commit |
| Serializable       | lowest             | none                        | predicate locks, SSI, or strict 2PL — retries and blocking |

## Real-World Examples

- **PostgreSQL**: default is Read Committed; `REPEATABLE READ` is actually snapshot isolation; `SERIALIZABLE` uses SSI (tracks rw-antidependencies, aborts cycles at commit).
- **MySQL InnoDB**: default is `REPEATABLE READ`, and stronger than the standard — *next-key locks* (row + gap locks on the index) eliminate phantoms, so InnoDB's RR is close to serializable for many range queries.
- **Oracle**: default is Read Committed. Its `SERIALIZABLE` is snapshot isolation, not true serializability — a footgun for developers porting from elsewhere.
- **CockroachDB / Google Spanner**: serializable by default. Spanner goes further (externally consistent, i.e., linearizable + serializable) using TrueTime.

## Common Pitfalls

- **Assuming isolation-level names are portable.** "REPEATABLE READ" means one thing in the SQL standard, a stronger thing in MySQL InnoDB, and "snapshot isolation" in PostgreSQL. Read the docs of the database you use.
- **Trusting snapshot isolation to prevent write skew.** It doesn't. If your correctness argument touches disjoint rows but relies on a shared invariant (on-call roster, bank-account sum, "at most N active users"), SI is not enough — use SERIALIZABLE, explicit `SELECT FOR UPDATE`, or a materialized conflict row that both transactions must write.
- **Confusing serializable with linearizable.** Serializable = *some* order exists. Linearizable = the real-time order is respected. A serializable database is allowed to return stale data to a reader who started *after* a writer committed, as long as the final history is equivalent to some serial order.
- **Picking isolation level per query.** Isolation is a property of a *transaction*, not a statement. Mixing levels across queries in the same transaction usually indicates a mental model that doesn't match what the engine actually does.

## See Also

- [[06-concurrency-control-strategies]] — the OCC, MVCC, and PCC families that actually implement these levels under the hood
- [[07-locks-latches-and-btree-concurrency]] — the locking and latching mechanics (predicate locks, next-key locks, 2PL) that make serializable enforceable on real B-trees
