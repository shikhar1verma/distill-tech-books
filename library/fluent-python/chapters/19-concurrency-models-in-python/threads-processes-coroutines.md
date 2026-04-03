---
title: "Threads, Processes, and Coroutines"
slug: threads-processes-coroutines
chapter: 19
book: "Fluent Python"
type: mixed
depends_on:
  - concurrency-vs-parallelism
tags: [threading, multiprocessing, asyncio, coroutines]
---

# Threads, Processes, and Coroutines

## The Three Execution Units

Python natively supports three kinds of execution units, each with distinct trade-offs.

### Processes

- An instance of the Python interpreter running in its own **isolated memory space**.
- Created via `multiprocessing.Process` or `concurrent.futures.ProcessPoolExecutor`.
- Communication requires **serialization** (pickling) across process boundaries.
- Enable **true parallelism** because each process has its own GIL.
- Preemptively scheduled by the OS.
- Highest startup cost.

### Threads

- Execution units **within** a single process, sharing the same memory.
- Created via `threading.Thread` or `concurrent.futures.ThreadPoolExecutor`.
- Shared memory makes data exchange easy but risky: concurrent writes can corrupt data without locks.
- Preemptively scheduled by the OS, but the GIL prevents CPU parallelism.
- Good for I/O-bound tasks: the GIL is released during syscalls (network, disk, `time.sleep`).

### Coroutines

- Functions defined with `async def` that can suspend and resume via `await`.
- Driven by an **event loop** (e.g., `asyncio`) in a single thread.
- Cooperative scheduling: a coroutine must explicitly `await` to let others run.
- Extremely lightweight -- you can have tens of thousands.
- No need for locks (only one coroutine runs at a time).
- Blocking calls (like `time.sleep`) freeze the entire event loop.

## Coordination Primitives

| Primitive | Purpose | Thread version | Process version | Asyncio version |
|---|---|---|---|---|
| Queue | Pass data between units | `queue.Queue` | `multiprocessing.Queue` | `asyncio.Queue` |
| Event | Simple signal flag | `threading.Event` | `multiprocessing.Event` | `asyncio.Event` |
| Lock | Mutual exclusion | `threading.Lock` | `multiprocessing.Lock` | `asyncio.Lock` |
| Semaphore | Limit concurrent access | `threading.Semaphore` | `multiprocessing.Semaphore` | `asyncio.Semaphore` |

## Code: Creating Each Type

```python
# Thread
from threading import Thread
t = Thread(target=my_func, args=(arg1, arg2))
t.start()
t.join()  # wait for completion

# Process
from multiprocessing import Process
p = Process(target=my_func, args=(arg1, arg2))
p.start()
p.join()

# Coroutine
import asyncio
async def my_coro():
    await asyncio.sleep(1)
    return 42

asyncio.run(my_coro())
```

## When to Use Which

- **I/O-bound, moderate concurrency** (tens of connections): `threading`
- **I/O-bound, high concurrency** (thousands of connections): `asyncio`
- **CPU-bound** (number crunching, image processing): `multiprocessing`
- **Mixed workloads**: combine asyncio with `loop.run_in_executor()` to offload CPU work to a process pool.

## Important Subtlety: Thread Termination

There is **no API to kill a thread** in Python. To stop a thread, you must:
1. Create a signaling mechanism (e.g., `threading.Event`).
2. Have the thread periodically check the signal.
3. Let it exit cleanly when signaled.

Coroutines, by contrast, can be cancelled via `Task.cancel()`, which raises `CancelledError` at the next `await` point -- a cleaner model.
