---
title: "Database Replication"
book: "System Design Interview"
chapter: 1
tags: [system-design, database, replication, availability, data-tier]
related:
  - "[[load-balancing]]"
  - "[[database-sharding]]"
  - "[[caching-strategies]]"
---

## Summary

Database replication uses a master/slave model to separate write and read operations. The master handles all writes; slaves receive copies of data and handle reads. Since most applications are read-heavy, this model improves performance by parallelizing reads across multiple slaves. It also provides reliability (data preserved across locations) and high availability (failover when a node goes down).

## How It Works

```mermaid
graph LR
    APP[Application] -->|INSERT, UPDATE, DELETE| MASTER[(Master DB)]
    APP -->|SELECT queries| SLAVE1[(Slave DB 1)]
    APP -->|SELECT queries| SLAVE2[(Slave DB 2)]

    MASTER -->|Replication stream| SLAVE1
    MASTER -->|Replication stream| SLAVE2
```

### Failover Scenarios

```mermaid
graph TB
    subgraph Slave Failure
        M1[(Master)] --> S1_OK[(Slave 1 - OK)]
        M1 -.->|offline| S1_FAIL[(Slave 2 - DOWN)]
        M1 -->|reads redirected| S1_OK
    end

    subgraph Master Failure
        S2_PROMOTE[(Slave 1 - Promoted)] -->|now accepts writes| APP2[Application]
        S2_NEW[(New Slave)] -->|replicate from| S2_PROMOTE
    end
```

**Slave fails:** Reads redirected to other slaves or temporarily to master. A new slave replaces the failed one.

**Master fails:** A slave is promoted to new master. Missing data updated via recovery scripts. A new slave is provisioned.

## When to Use

- Read-heavy workloads (most web applications)
- When high availability is required for the data tier
- When data durability across geographic locations matters
- When you need to scale read throughput beyond a single database

## Trade-offs

| Benefit | Cost |
|---------|------|
| Improved read performance | Replication lag (eventual consistency) |
| High availability via failover | Promotion complexity for master failure |
| Data redundancy across locations | More servers to manage |
| Read scaling is nearly linear | Write throughput still limited to master |

## Real-World Examples

- **MySQL:** Built-in master-slave replication; used by Facebook, Twitter
- **PostgreSQL:** Streaming replication with synchronous/asynchronous modes
- **Amazon RDS:** Managed read replicas across availability zones
- **Netflix:** Multi-region asynchronous replication for global availability

## Common Pitfalls

- Assuming replication is instantaneous -- there is always some lag
- Not testing master failover procedures before they are needed
- Reading from slaves for operations that require the latest data
- Having only one slave -- you lose read scaling during failover
- Not monitoring replication lag as a key metric

## See Also

- [[load-balancing]] -- Distributes read queries across slave databases
- [[database-sharding]] -- Horizontal data partitioning for write scaling
- [[caching-strategies]] -- Reduces read load on both master and slaves
