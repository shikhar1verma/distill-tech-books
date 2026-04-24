---
title: "Unix Tools as the Foundation of Batch Processing"
book: "Designing Data-Intensive Applications"
chapter: 11
sequence: 1
tags: [system-design, batch-processing, unix, data-pipelines]
related:
  - "[[02-distributed-storage-for-batch]]"
  - "[[04-mapreduce]]"
  - "[[06-shuffle-and-distributed-joins]]"
---

# Unix Tools as the Foundation of Batch Processing

> **One-sentence summary.** A batch job transforms immutable inputs into freshly generated outputs with no side effects, and a humble Unix pipeline of `awk | sort | uniq | head` already embodies the two execution strategies — in-memory hash aggregation and external-merge sorting — that distributed batch frameworks later generalize to a cluster.

## How It Works

The canonical example from *Designing Data-Intensive Applications* is finding the five most popular pages from an NGINX access log:

```bash
cat /var/log/nginx/access.log \
  | awk '{print $7}' \
  | sort \
  | uniq -c \
  | sort -r -n \
  | head -n 5
```

Each stage is a tiny, focused program connected by an OS pipe:

```mermaid
graph LR
  A[access.log] --> B[cat: stream lines]
  B --> C["awk: project URL field"]
  C --> D["sort: group equal keys adjacently"]
  D --> E["uniq -c: count runs"]
  E --> F["sort -rn: rank by count"]
  F --> G["head -n 5: top K"]
```

`cat` streams the file, `awk '{print $7}'` projects the requested URL, `sort` brings identical URLs next to each other, `uniq -c` collapses runs into `<count> <url>` rows, the second `sort -rn` ranks by count descending, and `head` truncates to the top five. The entire composition works because every stage reads newline-delimited records from stdin and writes them to stdout — a uniform interface that makes arbitrary reordering and substitution possible.

An equivalent Python program replaces the pipeline with a `collections.defaultdict(int)` keyed by URL, increments the counter per line, and then sorts the dictionary items. Both solutions compute the same answer, but they do so with fundamentally different memory and I/O profiles — and that difference is the whole point of the section.

## The Core Insight: Sort vs Hash Aggregation

The Python version keeps a **hash table** whose size is proportional to the number of **distinct** URLs, not the number of log lines. One million hits to `/favicon.ico` still occupy a single slot. The Unix pipeline keeps **no** aggregation state in memory; it instead physically sorts all records so that duplicates become adjacent, then counts adjacent runs.

| Dimension | In-memory hash (`defaultdict`) | External-merge sort (`sort \| uniq -c`) |
|-----------|-------------------------------|-----------------------------------------|
| Working set | Number of distinct keys | Bounded by disk, not RAM |
| Wins when | Distinct keys fit in RAM | Distinct keys exceed RAM |
| Access pattern | Random (hash probes) | Sequential (great for HDDs and SSDs) |
| Parallelism | Single process | GNU Coreutils `sort` auto-parallelizes across cores |
| Spill behavior | OOM kill | Writes sorted runs to disk, merges them |

GNU Coreutils `sort` transparently spills runs to disk and performs k-way merges, which is the same log-structured merge idea reused throughout storage engines. The upshot: the Unix pipeline scales from a 10 MB log to a 100 GB log on the same laptop with no code change, limited mainly by disk bandwidth. This sort-vs-hash dichotomy is not a Unix curiosity — it is the exact trade-off that [[04-mapreduce]] and [[06-shuffle-and-distributed-joins]] later replay at cluster scale.

## Why Batch Processing Has These Properties

A batch job reads read-only inputs and produces outputs generated from scratch on every run. That discipline yields several compounding benefits:

- **Human fault tolerance.** A bug in the code is recoverable by rolling the code back and rerunning — the inputs are untouched. Transactional systems lack this; bad writes mutate the source of truth.
- **Minimizing irreversibility.** Because mistakes are cheap, teams can ship more aggressively.
- **Reusable inputs.** The same input files feed multiple consumers: the main job, monitoring jobs that diff today's output against yesterday's, experimental variants.
- **Resource efficiency.** Sequential scans of large files use CPU and disk far more efficiently than the random I/O of an OLTP database.
- **Clean output switchover.** Keep the old output directory; point consumers at the new one. Revert by flipping the pointer back.

## When to Use

| Workload | Latency target | Input lifecycle | Typical tool |
|----------|---------------|-----------------|--------------|
| Batch (offline) | Minutes to hours | Bounded, reread on rerun | Unix pipes, Spark, Flink batch |
| Online (request/response) | Milliseconds | Mutable, queried per request | Databases, caches |
| Stream | Seconds | Unbounded, append-only | Kafka consumers, Flink streaming |

Reach for batch when throughput beats latency, when output can be regenerated, and when a long-running job on bounded input is acceptable — nightly ETL, ad pipelines, payroll, US banking ACH, training-set preparation.

## Trade-offs

| Aspect | Advantage | Disadvantage |
|--------|-----------|--------------|
| Immutable inputs | Time-travel recovery, safe reruns | Storage overhead; every rerun re-reads the whole input |
| Batch over online | High throughput, efficient resource use | Output visible only after job completes |
| Unix pipelines | Composable, stream-sequential, near-zero setup | Single machine; no network sharding |
| Sort-based aggregation | Works on larger-than-RAM data | Must materialize and sort the full stream |
| Hash aggregation | Single pass, no sort | Fails when distinct keys exceed RAM |

## Real-World Examples

- **Ad and payment pipelines** — the original motivating workloads behind MapReduce's adoption, built on shell tools and log files before cluster frameworks.
- **Nightly ETL into a warehouse** — a classic batch job: read raw logs, transform, write partitioned Parquet, swap the view.
- **US banking ACH** — interbank settlement still runs as a batch job; transactions submitted during the day settle overnight.
- **"Command-Line Tools Can Be 235x Faster than Your Hadoop Cluster"** — Adam Drake's well-known demonstration that `awk`, `sort`, and `xargs` on a laptop beat a small Hadoop cluster for many medium-sized analyses, precisely because a tuned single machine avoids coordination overhead.

## Common Pitfalls

- **Scaling a single-machine pipeline past its disk.** Unix `sort` is brilliant until the intermediate spill exceeds local storage; that is the exact point to move to [[02-distributed-storage-for-batch]].
- **`uniq` without a prior `sort`.** `uniq` only deduplicates **adjacent** lines; unsorted input silently produces wrong counts.
- **Line-oriented assumptions breaking on embedded newlines.** CSV fields, JSON blobs, or log messages containing `\n` fracture when passed through line-based tools. Parse with a format-aware tool (`jq`, `csvkit`) before piping.
- **Treating `cat file | cmd` as required.** `cmd < file` or `cmd file` is often cheaper; `cat` is used in pipelines only to make the left-to-right reading order visible.
- **Writing to external databases from batch jobs.** That reintroduces side effects and destroys the rerunnability that makes batch safe in the first place.

## See Also

- [[02-distributed-storage-for-batch]] — what replaces the local filesystem once a single disk is no longer enough.
- [[03-distributed-job-orchestration]] — what replaces the OS scheduler when pipes span machines.
- [[04-mapreduce]] — generalizes `sort | uniq -c` into a cluster-scale shuffle-and-reduce primitive.
- [[06-shuffle-and-distributed-joins]] — where the sort-vs-hash trade-off reappears as sort-merge joins versus broadcast hash joins.
- [[07-serving-derived-data-from-batch]] — how immutable batch outputs get handed back to online systems.
