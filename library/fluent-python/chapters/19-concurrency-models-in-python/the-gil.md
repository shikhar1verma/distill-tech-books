---
title: "The Global Interpreter Lock (GIL)"
slug: the-gil
chapter: 19
book: "Fluent Python"
type: theory-heavy
depends_on:
  - threads-processes-coroutines
tags: [GIL, CPython, threading, performance]
---

# The Global Interpreter Lock (GIL)

## What Is the GIL?

The Global Interpreter Lock is a mutex in CPython that allows only **one thread to execute Python bytecode at any time**, regardless of the number of CPU cores.

It exists because CPython's memory management (reference counting + garbage collection) is not thread-safe. The GIL makes the interpreter simpler, faster on a single core, and easier to extend via the C API.

## The 10 Key Points

1. Each Python interpreter is a **process**. Additional processes via `multiprocessing`.
2. The interpreter uses a **single thread** for user code and garbage collection.
3. The GIL means only **one thread runs Python code** at a time.
4. Python pauses the running thread every **~5ms** (`sys.getswitchinterval()`) to release the GIL.
5. Built-in functions and C extensions **can release the GIL** while running.
6. **All syscalls** (disk I/O, network I/O, `time.sleep`) release the GIL.
7. C extensions can spawn GIL-free threads that work with buffer-protocol objects (e.g., NumPy arrays).
8. For **network I/O**, threading works well -- threads spend most time waiting, so GIL contention is low.
9. For **CPU-intensive** Python code, the GIL makes threading **worse** than sequential.
10. For CPU parallelism, use **multiple processes** (each has its own GIL).

## The GIL Switch Interval

```python
import sys
print(sys.getswitchinterval())  # 0.005 (5 milliseconds)
# sys.setswitchinterval(0.01)  # change it (rarely needed)
```

Every 5ms, the bytecode interpreter forces the running thread to release the GIL. Other waiting threads then compete for it. This is why a simple spinner animation works with threading even during CPU-bound work -- the spinner thread gets a brief turn every 5ms.

## When the GIL Does NOT Matter

- **I/O-bound** threads: the GIL is released during every syscall, so threads waiting on network or disk do not block each other.
- **C extensions** (NumPy, zlib, bz2): release the GIL during heavy computation.
- **Coroutines**: run in a single thread, so the GIL is irrelevant -- there is nothing to contend.
- **System administration scripts**: mostly launching subprocesses and network calls.

## When the GIL IS the Bottleneck

- **CPU-intensive pure Python** with multiple threads: threads contend for the GIL, and context switching adds overhead. The result is **slower than sequential** code.
- Two or more threads both trying to crunch numbers in Python.

## Practical Implications

| Workload | Threading | Multiprocessing | asyncio |
|---|---|---|---|
| Network I/O | Good | Overkill | Best |
| Disk I/O | Good | Good | Good (with aiofiles) |
| CPU-bound Python | Bad (worse than sequential) | Good (true parallelism) | Bad (blocks event loop) |
| CPU-bound C extension | Good (GIL released) | Good | N/A |

## The Future of the GIL

- The GIL is a **CPython** implementation detail, not part of the Python language spec.
- Jython and IronPython have no GIL (but lag behind on Python version support).
- PyPy has a GIL.
- PEP 703 (accepted in principle) proposes making the GIL optional in CPython ("free-threaded Python"). Python 3.13+ includes experimental free-threaded builds.
- Eric Snow's PEP 554 proposes multiple subinterpreters in the stdlib, each with its own GIL.

## David Beazley's Quote

> "Python threads are great at doing nothing."

This perfectly captures the GIL's nature: threads that spend most of their time waiting (on I/O, on timers) work beautifully. Threads that want to compute burn time fighting the GIL.
