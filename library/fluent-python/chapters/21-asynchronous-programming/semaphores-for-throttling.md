---
title: "Semaphores for Throttling Concurrent Requests"
slug: semaphores-for-throttling
chapter: 21
book: fluent-python
type: concept
depends_on: [native-coroutines-and-async-await, async-context-managers]
tags: [semaphore, throttling, concurrency, asyncio, bounded-semaphore]
---

# Semaphores for Throttling Concurrent Requests

## Core Idea

An `asyncio.Semaphore` is a synchronization primitive that limits how many coroutines can hold it concurrently. Invented by Edsger Dijkstra in the early 1960s, the semaphore is flexible enough to implement locks, barriers, and other synchronization objects on top of it. Python provides three implementations: one each in `threading`, `multiprocessing`, and `asyncio`.

In async programming, semaphores solve a critical practical problem: **throttling concurrent network requests** so you do not overwhelm the server or violate rate limits. Unlike `ThreadPoolExecutor` (which naturally limits concurrency via `max_workers`), asyncio can spawn thousands of coroutines instantly -- a semaphore acts as the brake.

## How It Works

A semaphore has an **internal counter** initialized to a maximum value:

```python
semaphore = asyncio.Semaphore(10)  # allow 10 concurrent holders
```

Two operations control access:

| Operation | Effect | Blocks? |
|---|---|---|
| `await semaphore.acquire()` | Decrement counter. If counter is 0, suspend until someone releases. | Yes (coroutine) |
| `semaphore.release()` | Increment counter. Wake one suspended acquirer. | No (plain method) |

The recommended usage is as an **async context manager**, which calls `acquire` on entry and `release` on exit:

```python
async with semaphore:
    # at most 10 coroutines can be here simultaneously
    image = await get_flag(client, cc)
```

This guarantees `release()` is called even if an exception occurs inside the block.

## The Flag-Download Pattern

In the book's `flags2_asyncio.py`, the semaphore is created once in `supervisor` and passed to every `download_one` coroutine:

```python
async def supervisor(cc_list, concur_req):
    semaphore = asyncio.Semaphore(concur_req)
    async with httpx.AsyncClient() as client:
        to_do = [download_one(client, cc, semaphore) for cc in cc_list]
        for coro in asyncio.as_completed(to_do):
            status = await coro
```

Inside `download_one`, the semaphore wraps only the network call:

```python
async def download_one(client, cc, semaphore):
    async with semaphore:
        image = await get_flag(client, cc)
    # semaphore released here -- file save does not count against the limit
    await asyncio.to_thread(save_flag, image, f'{cc}.gif')
```

**Best practice:** hold the semaphore for the shortest possible time. Release it before doing file I/O or other work that does not need throttling.

## Multiple Requests per Task

When a task makes multiple network requests, use the semaphore separately for each:

```python
async def download_one(client, cc, semaphore):
    async with semaphore:
        image = await get_flag(client, cc)      # request 1
    async with semaphore:
        country = await get_country(client, cc)  # request 2
    await asyncio.to_thread(save_flag, image, f'{country}.gif')
```

Each `async with semaphore` independently acquires and releases, so the overall concurrency limit is respected even across multiple HTTP requests within the same logical task.

## BoundedSemaphore

The standard `Semaphore` allows `release()` to be called more times than `acquire()`, which increases the counter beyond its initial value. This is a bug in most programs. `BoundedSemaphore` enforces the constraint:

```python
sem = asyncio.BoundedSemaphore(3)
await sem.acquire()
sem.release()
sem.release()  # raises ValueError: BoundedSemaphore released too many times
```

Use `BoundedSemaphore` when you want to catch programming errors early. Use regular `Semaphore` when the counter needs to grow dynamically (rare in practice).

## Semaphore vs. Other Throttling

| Approach | Mechanism | When to use |
|---|---|---|
| `asyncio.Semaphore` | Limits concurrent coroutines | asyncio programs |
| `ThreadPoolExecutor(max_workers=N)` | Limits concurrent threads | Thread-based concurrency |
| Rate-limit tokens / leaky bucket | Limits requests per time window | API rate limiting |

The semaphore controls **concurrent access** (how many at once), not **throughput** (how many per second). For rate limiting, you may need a token bucket or a library like `aiolimiter`.

## Python's Three Semaphore Classes

All three classes in the standard library share the same API:

| Module | Class | Used with |
|---|---|---|
| `asyncio` | `asyncio.Semaphore` | Coroutines |
| `threading` | `threading.Semaphore` | Threads |
| `multiprocessing` | `multiprocessing.Semaphore` | Processes |

The asyncio version uses `await` for `acquire()` and is an async context manager. The threading version blocks the calling thread on `acquire()`. The multiprocessing version works across process boundaries using OS-level primitives.

## See Also

- [[asyncio-event-loop-and-http]] -- the download examples that use semaphores
- [[async-context-managers]] -- semaphores as async context managers
- [[async-vs-threads-and-pitfalls]] -- why throttling matters for async I/O
