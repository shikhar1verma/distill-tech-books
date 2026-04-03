---
title: "The concurrent.futures Package"
slug: concurrent-futures-overview
chapter: 20
book: fluent-python
type: mixed
depends_on: []
tags: [concurrency, concurrent-futures, executor, threads, processes]
---

# The `concurrent.futures` Package

## Core Idea

The `concurrent.futures` module (added in Python 3.2 via PEP 3148) provides a **high-level interface** for asynchronously executing callables using pools of threads or processes. It encapsulates the pattern Michele Simionato described: "spawning a bunch of independent threads and collecting the results in a queue."

Instead of managing threads, locks, and queues yourself, you use an **Executor** that handles all that infrastructure.

## The Two Executors

| Class | Worker type | Best for | Default `max_workers` |
|---|---|---|---|
| `ThreadPoolExecutor` | OS threads | I/O-bound (HTTP, file I/O, DB) | `min(32, os.cpu_count() + 4)` |
| `ProcessPoolExecutor` | OS processes | CPU-bound (bypasses GIL) | `os.cpu_count()` |

Both implement the same `Executor` abstract interface, so switching between them is usually a one-line change.

## Key Methods

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    # Parallel map -- results in submission order
    results = executor.map(fn, iterable)

    # Submit individual tasks -- returns Future objects
    future = executor.submit(fn, arg1, arg2)
```

- **`executor.map(fn, *iterables)`** -- parallel version of the built-in `map()`. Returns an iterator yielding results in submission order.
- **`executor.submit(fn, *args, **kwargs)`** -- schedules a single callable and returns a [[future-objects|Future]] object.
- **Context manager** -- `executor.__exit__` calls `shutdown(wait=True)`, blocking until all workers finish.

## Why It Matters

The `concurrent.futures` design philosophy is that concurrency infrastructure (threads, processes, queues, worker management) should be **invisible to application code**. You express *what* to compute in parallel; the executor handles *how*.

This makes it straightforward to add concurrency on top of existing sequential code: extract the loop body into a function, then pass it to `executor.map`.

## See Also

- [[thread-pool-executor]] -- ThreadPoolExecutor and `executor.map` in depth
- [[future-objects]] -- Future objects, `submit`, `result`, and `as_completed`
- [[process-pool-executor]] -- ProcessPoolExecutor for CPU-bound work
