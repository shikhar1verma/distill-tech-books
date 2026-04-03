---
title: "Async vs Threads and CPU-Bound Pitfalls"
slug: async-vs-threads-and-pitfalls
chapter: 21
book: fluent-python
type: concept
depends_on: [native-coroutines-and-async-await, asyncio-event-loop-and-http]
tags: [async, threads, cpu-bound, event-loop, performance, curio, trio, structured-concurrency]
---

# Async vs Threads and CPU-Bound Pitfalls

## Core Idea

Asynchronous programming excels at **I/O-bound concurrency** in a single thread because network and disk operations are orders of magnitude slower than CPU and RAM operations. But the chapter's most important lesson is a warning: **there are no truly "I/O-bound systems" -- only I/O-bound functions.** Every nontrivial system has CPU-bound parts, and if any of them run inside a coroutine, they block the event loop and degrade performance for every concurrent task.

## Why Async Works: The Latency Gap

Ryan Dahl (inventor of Node.js) presents these numbers that explain why async I/O is so effective:

| Device | CPU cycles | Human-scale equivalent |
|---|---|---|
| L1 cache | 3 | 3 seconds |
| L2 cache | 14 | 14 seconds |
| RAM | 250 | 250 seconds |
| Disk | 41,000,000 | 1.3 years |
| Network | 240,000,000 | 7.6 years |

While a coroutine waits for a network response (7.6 "years"), the event loop can execute hundreds of millions of CPU instructions, driving other coroutines. This is why a single-threaded async server can handle thousands of concurrent connections.

## The Myth of I/O-Bound Systems

The author learned the hard way that labeling an entire system as "I/O-bound" is dangerous. You may have I/O-bound *functions* -- and most of them probably are -- but inevitably, nontrivial systems contain CPU-bound code.

The chapter tells two cautionary tales:

### The uvloop Benchmarks

Yury Selivanov created uvloop, a fast drop-in replacement for asyncio's event loop. His benchmarks showed performance "close to Go" -- but only after he also created `httptools`, a Python binding for Node.js's HTTP parser written in C. The Python HTTP parser in `aiohttp` was so CPU-intensive that it blocked the event loop enough to negate uvloop's speed advantage. Even a "simple echo server" -- the canonical "I/O-bound" example -- was bottlenecked by CPU-bound header parsing.

### Death by a Thousand Cuts

A large async system built with Twisted was gradually slowing down. No single function was the bottleneck. Instead, months of feature development had sprinkled CPU-bound data parsing and format conversion throughout the codebase. Each function was small, but collectively they starved the event loop. Fixing it would have required rearchitecting the system -- the project was cancelled instead.

## Dealing with CPU-Bound Code

When you identify a CPU-hogging bottleneck:

1. **Delegate to a ProcessPoolExecutor.** Runs in a separate process, bypassing the GIL:
   ```python
   loop = asyncio.get_running_loop()
   result = await loop.run_in_executor(process_pool, cpu_heavy_fn, args)
   ```

2. **Use an external task queue** (Celery, RQ, Dramatiq). Choose and integrate this at project start so the team uses it naturally.

3. **Rewrite in C, Cython, or Rust** with GIL release. This is what Selivanov did with `httptools`.

4. **Accept the cost** and do nothing -- but document it as tech debt so you can revisit the decision later.

Glyph Lefkowitz (founder of Twisted) says one of his priorities at the start of any async project is to **decide which tools to use for farming out CPU-intensive tasks**, before the first line of application code is written.

## Structured Concurrency

Traditional asyncio uses `gather` and `create_task` for ad-hoc concurrency, but these can lead to tasks that outlive their parent scope, making error handling and cleanup difficult. **Structured concurrency** constrains all concurrent tasks to a single entry and exit point -- analogous to structured programming replacing `GOTO` with block statements.

David Beazley's **Curio** framework pioneered this in Python with `TaskGroup`:

```python
async with TaskGroup() as group:
    for domain in domains:
        await group.spawn(probe, domain)
    async for task in group:
        domain, found = task.result
```

The `TaskGroup` ensures that all spawned tasks are completed or cancelled when the block exits. If any task raises an exception, remaining tasks are cancelled and the exception propagates.

Nathaniel J. Smith's **Trio** framework further developed structured concurrency with "nurseries." The success of these ideas led to PEP 654 (Exception Groups and `except*`) in Python 3.11, and `asyncio.TaskGroup` was added in Python 3.11 as well.

## async Beyond asyncio: Curio

Python's `async`/`await` keywords are **not tied to asyncio**. Anyone can write their own event loop. Curio demonstrates this with a cleaner, simpler API:

```python
from curio import run, TaskGroup
import curio.socket as socket

async def probe(domain: str) -> tuple[str, bool]:
    try:
        await socket.getaddrinfo(domain, None)
    except socket.gaierror:
        return (domain, False)
    return (domain, True)
```

Notable Curio features:
- `TaskGroup` replaces `gather`, `as_completed`, and ad-hoc task management
- `spawn_thread(func)` for easy thread integration
- `UniversalQueue` for communication between coroutines and threads
- `AWAIT(coro)` function for calling coroutines from threads (all-caps because `await` is a keyword)

## Async vs. Threads: When to Choose Which

| Factor | Async (asyncio) | Threads |
|---|---|---|
| Best for | Many concurrent I/O operations | Mixed I/O with some blocking libraries |
| Concurrency model | Cooperative (explicit `await`) | Preemptive (OS schedules) |
| Shared state | Safe (single thread, no locks needed for coroutine-local data) | Requires locks |
| Scalability | Thousands of connections easily | Hundreds of threads (OS limit) |
| Ecosystem | Requires async libraries | Works with any library |
| Debugging | Stack traces can be confusing | More familiar tracebacks |
| CPU-bound work | Blocks the event loop | Blocked by GIL |

The "What Color Is Your Function?" essay by Bob Nystrom captures the fundamental tension: async and sync functions are incompatible "colors." Once you introduce async, it propagates through your codebase. Go avoids this by making all functions the same "color" via goroutines -- but Go has its own tradeoffs (as Nathaniel Smith argues in "Go statement considered harmful").

## Key Recommendations

1. **Start with async infrastructure early.** Adding it later is painful (the all-or-nothing problem).
2. **Set up a task queue from day one.** Do not wait until you discover CPU bottlenecks.
3. **Write performance regression tests** that detect when async code gets slower. By the time humans notice, it is too late.
4. **Hold semaphores briefly** and delegate blocking calls to threads.
5. **Profile regularly** -- there are no I/O-bound systems, only I/O-bound functions.

## See Also

- [[native-coroutines-and-async-await]] -- the all-or-nothing problem explained
- [[semaphores-for-throttling]] -- managing concurrent access
- [[asyncio-event-loop-and-http]] -- practical download patterns with asyncio
