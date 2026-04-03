---
title: "ThreadPoolExecutor and executor.map"
slug: thread-pool-executor
chapter: 20
book: fluent-python
type: code-heavy
depends_on:
  - concurrent-futures-overview
tags: [concurrency, threads, thread-pool, executor-map, io-bound]
---

# ThreadPoolExecutor and `executor.map`

## Core Idea

`ThreadPoolExecutor` runs callables concurrently in a managed pool of OS threads. The simplest usage is `executor.map(fn, iterable)`, which is the concurrent equivalent of `map(fn, iterable)` -- results come back in **submission order**.

This is ideal for **I/O-bound** tasks like downloading files, making HTTP requests, or reading from databases, where threads spend most of their time waiting.

## Minimal Example: Sequential to Concurrent

The book shows a flag-downloading script. Here is the key refactoring pattern:

```python
# BEFORE: sequential
def download_many(cc_list):
    for cc in sorted(cc_list):
        image = get_flag(cc)
        save_flag(image, f'{cc}.gif')
    return len(cc_list)

# AFTER: concurrent (one-line change in logic)
from concurrent.futures import ThreadPoolExecutor

def download_many(cc_list):
    with ThreadPoolExecutor() as executor:
        res = executor.map(download_one, sorted(cc_list))
    return len(list(res))
```

The body of the `for` loop becomes a standalone function (`download_one`), and `executor.map` runs it across all items in parallel.

## `max_workers` Configuration

```python
# Default since Python 3.8:
max_workers = min(32, os.cpu_count() + 4)
```

The rationale: preserve at least 5 workers for I/O-bound tasks, cap at 32 to avoid excessive resource usage on many-core machines. `ThreadPoolExecutor` also reuses idle workers before spawning new ones.

For I/O-bound work, you can safely increase `max_workers` well beyond CPU count (e.g., 100 concurrent HTTP requests). For CPU-bound work, extra threads beyond the core count add overhead without benefit due to the GIL.

## Results and Exceptions in `executor.map`

- Results are yielded in **submission order** (not completion order).
- If a callable raises an exception, that exception is raised when `next()` is called on the results iterator at the position corresponding to that task.
- This means an early exception can block you from seeing results of later tasks that succeeded.

For finer control over error handling and result ordering, use [[future-objects|executor.submit + as_completed]] instead.

## Performance: The Flags Benchmark

From the book's experiment with 20 flag downloads:

| Approach | Avg time |
|---|---|
| Sequential (`flags.py`) | ~7.2s |
| `ThreadPoolExecutor` (`flags_threadpool.py`) | ~1.4s |
| `asyncio` (`flags_asyncio.py`) | ~1.35s |

Threads and asyncio perform comparably for HTTP clients; both achieve **5x+ speedup** over sequential code. The difference grows larger with more downloads.

## See Also

- [[concurrent-futures-overview]] -- The package overview
- [[executor-map-behavior]] -- Deep dive into `executor.map` ordering and blocking
- [[future-objects]] -- Lower-level control with `submit` and `as_completed`
