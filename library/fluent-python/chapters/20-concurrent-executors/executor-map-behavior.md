---
title: "Executor.map Ordering and Blocking Behavior"
slug: executor-map-behavior
chapter: 20
book: fluent-python
type: mixed
depends_on:
  - thread-pool-executor
  - future-objects
tags: [concurrency, executor-map, ordering, blocking, generator]
---

# `Executor.map` Ordering and Blocking Behavior

## Core Idea

`executor.map` returns a **generator** that yields results in **submission order**. Internally, it creates a Future for each call; when you iterate, `__next__` calls `future.result()` on each future in sequence. If the first submitted task is the slowest, iteration **blocks** until it completes -- even if all other tasks finished long ago.

This is a critical behavioral detail that determines whether `executor.map` or `submit` + `as_completed` is the right tool for your use case.

## The `demo_executor_map.py` Experiment

The book demonstrates this with a `loiter(n)` function that sleeps for `n` seconds, submitted as `loiter(0), loiter(1), ..., loiter(4)` to a pool of 3 workers:

```
[15:56:50] loiter(0): doing nothing for 0s...   # starts immediately
[15:56:50] loiter(0): done.
[15:56:50]   loiter(1): doing nothing for 1s...  # starts immediately
[15:56:50]     loiter(2): doing nothing for 2s... # starts immediately
[15:56:50] results: <generator object ...>        # non-blocking!
[15:56:50]       loiter(3): doing nothing for 3s...  # starts when loiter(0) frees a worker
[15:56:50] result 0: 0                            # available immediately
[15:56:51]   loiter(1): done.
[15:56:51]         loiter(4): doing nothing for 4s...
[15:56:51] result 1: 10                           # available at 1s
[15:56:52]     loiter(2): done.
[15:56:52] result 2: 20                           # available at 2s
```

Key observations:
1. The `executor.map` call itself is **non-blocking** -- it returns a generator immediately.
2. Iterating the generator blocks on each result **in order**.
3. If `loiter(0)` had taken 10 seconds, you would see no results for 10 seconds, even though `loiter(1)` through `loiter(4)` might finish sooner.

## When This Matters

**`executor.map` is ideal when:**
- You want results in a predictable, deterministic order.
- All tasks take roughly the same time.
- You don't need per-task error handling or progress display.

**Use `submit` + `as_completed` instead when:**
- You need to show progress as tasks complete (e.g., with tqdm).
- Task durations vary widely and you want fast results first.
- You need per-task error handling with contextual information.
- You want to submit different callables (not just one function across items).

## The Blocking Problem in Practice

For the prime-checker example, numbers sorted in descending order means the second number (a massive prime) blocks the display for ~9.5 seconds. All other results are ready but cannot be shown because `executor.map` yields in order.

```python
# This blocks on the slow prime while fast composites wait
for n, prime, elapsed in executor.map(check, sorted_descending):
    print(f"{n}: {elapsed:.2f}s")
```

With `as_completed`, results would appear as each check finishes, giving visible progress.

## See Also

- [[thread-pool-executor]] -- `executor.map` basics
- [[future-objects]] -- `submit` + `as_completed` for out-of-order results
- [[error-handling-concurrent]] -- Real-world patterns combining `as_completed` with error handling
