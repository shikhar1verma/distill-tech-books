---
title: "ProcessPoolExecutor for CPU-Bound Work"
slug: process-pool-executor
chapter: 20
book: fluent-python
type: code-heavy
depends_on:
  - concurrent-futures-overview
tags: [concurrency, processes, cpu-bound, GIL, multiprocessing, parallelism]
---

# ProcessPoolExecutor for CPU-Bound Work

## Core Idea

`ProcessPoolExecutor` distributes work across **separate OS processes**, each with its own Python interpreter and GIL. This provides true parallelism for CPU-bound tasks, unlike `ThreadPoolExecutor` where the GIL serializes CPU work.

Because both executors share the `Executor` interface, switching is trivial:

```python
# Just change the class name:
# with ThreadPoolExecutor() as executor:
with ProcessPoolExecutor() as executor:
    results = executor.map(cpu_heavy_fn, data)
```

## When to Use Processes vs Threads

| Factor | `ThreadPoolExecutor` | `ProcessPoolExecutor` |
|---|---|---|
| I/O-bound tasks | Excellent | Works, but overkill |
| CPU-bound tasks | Limited by GIL | True parallelism |
| Memory overhead | Low (shared memory) | High (separate process) |
| Startup time | Fast | Slower |
| Data sharing | Easy (shared state) | Requires serialization (pickle) |
| Default workers | `min(32, cpu_count + 4)` | `os.cpu_count()` |

**Rule of thumb:** Use threads for I/O, processes for CPU.

## The Multicore Prime Checker

The book shows a prime-checking example. With `multiprocessing` directly (43 lines), it requires managing `SimpleQueue`, worker functions, and process lifecycle. With `ProcessPoolExecutor` (31 lines), all that infrastructure is hidden:

```python
import sys
from concurrent import futures
from time import perf_counter

def check(n: int) -> tuple[int, bool, float]:
    t0 = perf_counter()
    result = is_prime(n)
    return (n, result, perf_counter() - t0)

def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else None
    with futures.ProcessPoolExecutor(workers) as executor:
        for n, prime, elapsed in executor.map(check, numbers):
            label = 'P' if prime else ' '
            print(f'{n:16}  {label} {elapsed:9.6f}s')
```

No `multiprocessing` import, no queues, no worker function boilerplate.

## `executor.map` Ordering Caveat with Processes

Results from `executor.map` come back in **submission order**. For the prime checker with numbers sorted in descending order, this means:

1. The second number (a large prime, ~9.5s to check) blocks the output.
2. Meanwhile, the remaining processes finish their easier tasks.
3. Once the slow result is ready, all remaining results appear immediately.

If you need results as they complete (e.g., for progress display), use `executor.submit()` with `as_completed()` instead.

## Constraints

- Arguments and return values must be **picklable** (serialized between processes).
- Higher memory usage: each process gets a full Python interpreter.
- `ProcessPoolExecutor` should **not** be used for I/O-bound tasks -- the overhead is unnecessary, and threads work fine for those.
- Works best for "embarrassingly parallel" problems where tasks are independent.

## See Also

- [[concurrent-futures-overview]] -- The package overview
- [[thread-pool-executor]] -- ThreadPoolExecutor for I/O-bound work
- [[executor-map-behavior]] -- Detailed discussion of `map` ordering behavior
