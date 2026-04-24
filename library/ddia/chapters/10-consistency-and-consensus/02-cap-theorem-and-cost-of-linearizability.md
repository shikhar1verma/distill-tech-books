---
title: "CAP Theorem and the Cost of Linearizability"
book: "Designing Data-Intensive Applications"
chapter: 10
sequence: 2
tags: [system-design, distributed-systems, cap-theorem, consistency, latency]
related:
  - "[[01-linearizability]]"
  - "[[03-logical-clocks]]"
  - "[[06-consensus-algorithms]]"
---

# CAP Theorem and the Cost of Linearizability

> **One-sentence summary.** CAP is often misquoted as "pick two of three" — the real statement is "either consistent *or* available *when partitioned*", and even without partitions, linearizability costs you latency proportional to network delay uncertainty.

## How It Works

Picture a multi-region deployment with replicas in two regions connected by a WAN link. Inside each region the network is fine; clients reach their local replicas without trouble. Then the WAN link breaks. This is a *network partition*, and it forces a choice that no implementation can avoid: the replicas that cannot reach each other must either refuse requests (to preserve a single global order of writes) or keep serving them from stale local state (to stay up). You cannot have both.

```mermaid
graph LR
  subgraph RegionA["Region A"]
    CA[Client A] --> RA[Replica A]
  end
  subgraph RegionB["Region B"]
    CB[Client B] --> RB[Replica B]
  end
  RA <-. WAN partition .-x RB
  RA --> CP["<b>CP choice</b><br/>linearizable, but<br/>B replicas unavailable"]
  RB --> AP["<b>AP choice</b><br/>stays up, but reads<br/>may be stale / diverge"]
```

That is [[01-linearizability]] in a nutshell: a single up-to-date copy of the data, from the client's point of view. The [[06-consensus-algorithms]] needed to maintain it (Paxos, Raft, ZAB) require a majority quorum to make progress, so any replica cut off from the majority must stop answering — hence "CP". A multi-leader or leaderless system avoids the quorum requirement by letting each replica accept writes independently and reconcile later, so it stays up during a partition — hence "AP".

This is the correct reading of CAP, and it is very narrow. The theorem considers *one* consistency model (linearizability) and *one* fault (network partition). It says nothing about dead nodes, GC pauses, skewed clocks, or — crucially — about the latency cost of linearizability on a *healthy* network. According to Google's own data, partitions cause fewer than 8% of incidents. Designing your whole storage stack around CAP alone is fitting a system to a rare edge case.

PACELC is the usual successor rule of thumb: during a **P**artition, pick **A** or **C**; **E**lse (no partition), pick **L**atency or **C**onsistency. It at least acknowledges that linearizability has a cost even when the network is fine, but it inherits CAP's awkward definitions of "consistency" and "availability" and still treats consistency as a single binary.

The deeper result is Attiya and Welch's lower bound: **the response time of linearizable reads and writes is at least proportional to the uncertainty of delays in the network.** No cleverer algorithm can fix this. A region that wants its write to be linearizable must wait long enough to be sure no concurrent write elsewhere has become visible — and in a network with unbounded jitter, "long enough" is long. This is why even RAM on a multi-core CPU is not linearizable by default: each core has its own cache, and making cross-core reads see the latest write requires explicit memory barriers. The cost there isn't a fear of partitions (you don't expect one CPU core to detach from the others); it's pure performance. The same logic applies to distributed databases that drop linearizability: they do it for latency, not for fault tolerance.

## When to Use This Framing

- **Justifying a multi-leader / leaderless design for multi-region writes.** Accepting the AP side lets every region serve writes locally; you owe the application a conflict-resolution story.
- **Budgeting the cost of a globally consistent datastore.** A linearizable cross-region write pays at least one WAN round-trip; a linearizable cross-region read does too. PACELC's "E/L" side is often the dominant cost in a well-run cluster.
- **Explaining to stakeholders why "strong consistency" isn't free in steady state.** The failure-time argument (availability during partition) is the tip; the latency bill is the iceberg.

## CAP vs PACELC vs the Actual Trade-off

| Framing | During a partition | On a healthy network | What it misses |
|---|---|---|---|
| CAP ("pick two of three") | Consistency *or* Availability | Silent — assumes both are free | Ignores latency, variable delays, weaker consistency models; partition tolerance isn't a choice |
| CAP (proper reading) | Either C or A, not both | Both achievable | Still only linearizability and partitions; binary view |
| PACELC | P → A vs C | E → L vs C | Inherits CAP's definitions; still a single consistency knob |
| Actual engineering trade-off | Bounded staleness vs outage per region | Per-operation latency vs recency, tunable per call | Requires per-workload judgement; no clean acronym |

## Real-World Examples

- **Spanner / CockroachDB / FoundationDB / TiDB**: CP-leaning. Globally linearizable (or close to it) via consensus + bounded-uncertainty clocks (Spanner's TrueTime). The cost shows up as a mandatory "commit wait" on every cross-region write, paid **all the time**, not just during faults.
- **etcd / ZooKeeper / Consul**: CP within a single cluster. Linearizable writes and reads via Raft/ZAB. Used for config, service discovery, leader election — small data, where the quorum latency is acceptable.
- **Cassandra / Riak / DynamoDB**: AP with tunable quorums. Default writes/reads are not linearizable; you can opt into stricter consistency per operation (e.g. `QUORUM`/`LOCAL_QUORUM`) and pay the latency only when needed. See [[03-logical-clocks]] for how they track causality without a global order.
- **Multi-region active-active multi-leader (e.g. BDR, CRDT-based stores)**: explicitly AP. Each region is a leader, writes replicate asynchronously, conflicts resolve via last-writer-wins or CRDT merge. Survives a WAN cut, but readers can see divergent state.
- **CockroachDB's default isolation**: serializable, but *not* strict serializable across regions out of the box — a conscious choice to avoid paying TrueTime-scale wait times on every commit.

## Common Pitfalls

- **Using CAP to justify NoSQL wholesale.** "We chose Cassandra because CAP" isn't an argument. Cassandra is AP *with tunable consistency*; the real decision is which operations need linearizability and which don't.
- **Conflating "partition tolerance" with "choosing availability".** Partitions happen regardless — the only way to avoid them is to run a single replica, which isn't high availability either. P is not a dial; A vs C is.
- **Assuming strong consistency only costs you during failures.** This is the biggest trap. Attiya–Welch says a linearizable system pays for network delay uncertainty on every request, healthy or not. If p99 WAN latency is your budget, linearizable cross-region reads will blow it.
- **Treating CAP's "availability" as the operational definition.** CAP's formal availability means "every non-failing node answers every request" — many systems marketed as highly available don't meet that bar and are neither strictly CP nor strictly AP.
- **Ignoring weaker consistency models.** Causal consistency, read-your-writes, and monotonic reads often give you 90% of what applications actually need at a fraction of the latency. CAP's binary C/not-C framing hides this entire design space.

## See Also

- [[01-linearizability]] — the exact consistency model CAP is talking about, and why "one copy of the data" is harder than it sounds.
- [[03-logical-clocks]] — how AP systems track causality without a global order, sidestepping the Attiya–Welch bound.
- [[06-consensus-algorithms]] — the machinery (Raft/Paxos) that actually enforces the CP side, and the quorum latency that makes it expensive.
