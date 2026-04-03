---
title: "Process Pools and the Multicore Prime Checker"
slug: multicore-prime-checker
chapter: 19
book: "Fluent Python"
type: code-heavy
depends_on:
  - the-gil
  - spinner-example
tags: [multiprocessing, SimpleQueue, process-pool, poison-pill, CPU-bound]
---

# Process Pools and the Multicore Prime Checker

## The Problem

Check primality for 20 large integers. Sequential execution takes ~40 seconds. Can we distribute the work across CPU cores?

## The Primality Test

```python
import math

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    root = math.isqrt(n)
    for i in range(3, root + 1, 2):
        if n % i == 0:
            return False
    return True
```

This is a simple trial-division algorithm. For `n = 5_000_111_000_222_021`, it takes about 3.3 seconds on a typical laptop.

## Architecture: Queues and Workers

The process pool pattern uses two queues:

```
   Main Process                Workers (N processes)
   ┌──────────┐     jobs       ┌─────────┐
   │ enqueue  │───────────────>│ worker 1 │──┐
   │ numbers  │     SimpleQ    │ worker 2 │  │  results
   │          │                │ worker N │──┼────────> Main collects
   │ enqueue  │                └─────────┘  │          and displays
   │ poison   │                             │
   │ pills    │                             │
   └──────────┘                             │
```

## The Worker Function

```python
from multiprocessing import Process, SimpleQueue, cpu_count
from typing import NamedTuple

class PrimeResult(NamedTuple):
    n: int
    prime: bool
    elapsed: float

def worker(jobs: SimpleQueue, results: SimpleQueue) -> None:
    while n := jobs.get():       # blocks until item available; 0 = stop
        results.put(check(n))
    results.put(PrimeResult(0, False, 0.0))  # "I'm done" signal
```

Key pattern elements:
- **Infinite loop** consuming from a queue -- the standard concurrent worker pattern.
- **Poison pill** (`0`) terminates the loop. `None` is another common sentinel, but `0` simplifies the `PrimeResult` type.
- **Done signal** sent back to the main process so it knows when all workers have exited.

## Starting Jobs

```python
def start_jobs(procs, jobs, results):
    for n in NUMBERS:
        jobs.put(n)          # enqueue all work items
    for _ in range(procs):
        jobs.put(0)          # one poison pill per worker
    for _ in range(procs):
        proc = Process(target=worker, args=(jobs, results))
        proc.start()
```

## Collecting Results

```python
def report(procs, results):
    checked = 0
    procs_done = 0
    while procs_done < procs:
        n, prime, elapsed = results.get()  # blocks until result available
        if n == 0:
            procs_done += 1    # one worker finished
        else:
            checked += 1
            label = 'P' if prime else ' '
            print(f'{n:16}  {label} {elapsed:9.6f}s')
    return checked
```

Results arrive in **completion order**, not submission order. That is why `PrimeResult` includes `n` -- without it, we could not match results to inputs.

## Performance Results

On a 6-core laptop (12 logical CPUs via hyperthreading):

| Approach | Time | Speedup |
|---|---|---|
| Sequential | ~40s | 1x |
| 6 processes | ~10s | ~4x |
| 12 processes | ~10s | ~4x (diminishing returns) |

The speedup is less than 6x because:
- Process startup and IPC add overhead.
- Hyperthreading helps less for compute-bound work (both threads share the same core's ALU).
- Work items are not equal size: the largest prime takes ~4.7s, creating a long tail.

## Sentinel Values and Poison Pills

Common sentinel patterns in concurrent programming:

| Sentinel | Pros | Cons |
|---|---|---|
| `0` | Simple, type-compatible | Cannot be used if `0` is valid data |
| `None` | Universal convention | Cannot survive pickling with identity |
| `Ellipsis` (`...`) | Survives pickling, rare in data | Uncommon convention |
| `object()` | Guaranteed unique | Does NOT survive pickling (loses identity) |

## Why Threading Fails Here

A threaded version of this program is **slower** than sequential, because:
1. All threads compete for the GIL every 5ms.
2. Context switching (saving/restoring CPU registers, cache invalidation) adds overhead.
3. More threads = more contention = slower execution.

This is the definitive proof that CPU-bound Python work must use processes, not threads.

## The Better Way: ProcessPoolExecutor

The `concurrent.futures.ProcessPoolExecutor` (Chapter 20) encapsulates this exact pattern:
- Manages the worker processes.
- Handles the job and result queues internally.
- Provides a clean `map()` / `submit()` API.
- More robust error handling.

```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor() as executor:
    results = executor.map(is_prime, NUMBERS)
```
