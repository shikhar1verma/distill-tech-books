---
title: Concurrency Control (Pessimistic, Optimistic, Constraints)
book: "System Design Interview Volume 2"
chapter: 7
tags: [system-design, concurrency, locking, optimistic-locking, pessimistic-locking, database-constraints]
related: [reservation-data-model, idempotent-reservation-api, database-sharding-and-caching]
---

## Summary

When multiple users attempt to book the last available room simultaneously, the system must prevent **double-booking**. Three approaches are compared: **pessimistic locking** (`SELECT ... FOR UPDATE`) serializes transactions but risks deadlocks and poor scalability; **optimistic locking** (version column) avoids locks but causes retry storms under high contention; **database constraints** (`CHECK total_inventory - total_reserved >= 0`) are the simplest approach and work well for hotel reservation systems where QPS is moderate.

## How It Works

```mermaid
graph TB
    subgraph Race["Race Condition - The Problem"]
        U1["User 1: reads 1 room left"]
        U2["User 2: reads 1 room left"]
        B1["User 1: reserves (total_reserved = 100)"]
        B2["User 2: reserves (total_reserved = 100)"]
        BAD["Both succeed -- double booking"]
    end

    U1 --> B1
    U2 --> B2
    B1 --> BAD
    B2 --> BAD

    subgraph Solutions["Three Solutions"]
        subgraph Pessimistic["Pessimistic Locking"]
            PL1["SELECT ... FOR UPDATE"]
            PL2["Lock acquired by User 1"]
            PL3["User 2 waits"]
            PL4["User 1 commits, lock released"]
            PL5["User 2 sees no rooms"]
        end

        subgraph Optimistic["Optimistic Locking"]
            OL1["Both read version = 1"]
            OL2["User 1 writes version = 2 -- success"]
            OL3["User 2 writes version = 2 -- conflict"]
            OL4["User 2 retries"]
        end

        subgraph Constraint["Database Constraint"]
            DC1["CHECK total_inventory minus total_reserved >= 0"]
            DC2["User 1 UPDATE succeeds"]
            DC3["User 2 UPDATE violates constraint"]
            DC4["Transaction rolled back"]
        end
    end
```

1. **Pessimistic locking**: `SELECT ... FOR UPDATE` locks the row; other transactions block until release
2. **Optimistic locking**: read the row with its version number; on write, check that version matches; if not, retry
3. **Database constraint**: a CHECK constraint rejects any UPDATE that would make `total_inventory - total_reserved < 0`
4. All three guarantee correctness, but differ in performance and complexity characteristics

## When to Use

| Approach | Best For |
|---|---|
| Pessimistic locking | Extremely high contention (rare in hotel systems) |
| Optimistic locking | Low-to-moderate contention, general-purpose systems |
| Database constraints | Simple systems with moderate QPS (hotel reservations) |

## Trade-offs

| Aspect | Benefit | Cost |
|---|---|---|
| Pessimistic locking | Prevents all conflicts | Deadlock risk; blocks concurrent access; not scalable |
| Optimistic locking | No locks; fast when contention is low | Retry storms when many users compete for same resource |
| Database constraints | Simplest to implement; DB enforces correctness | Not portable across all databases; hard to version-control |
| No concurrency control | Maximum throughput | Double-booking, data corruption |
| Serializable isolation | Strongest guarantee | Severe performance penalty |

## Real-World Examples

- **Hotel reservation systems**: typically use optimistic locking or DB constraints due to low QPS
- **Airline seat selection**: pessimistic locking for individual seat maps (high contention on popular flights)
- **E-commerce flash sales**: optimistic locking with retries or Redis-based distributed locks
- **Banking transfers**: pessimistic locking or serializable transactions for financial integrity

## Common Pitfalls

- Using pessimistic locking for hotel reservations (overkill -- QPS is ~3, not 30,000)
- Not setting lock timeouts with pessimistic locking (can cause indefinite blocking)
- Optimistic locking without a retry limit (infinite retry loops under high contention)
- Assuming database constraints are supported by all databases (some NoSQL databases lack CHECK constraints)

## See Also

- [[reservation-data-model]] -- the inventory table that these locking strategies protect
- [[idempotent-reservation-api]] -- preventing duplicate inserts from the same user
- [[database-sharding-and-caching]] -- how sharding affects locking scope
