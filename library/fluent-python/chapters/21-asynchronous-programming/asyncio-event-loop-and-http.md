---
title: "The asyncio Event Loop and Downloading with HTTPX"
slug: asyncio-event-loop-and-http
chapter: 21
book: fluent-python
type: concept
depends_on: [native-coroutines-and-async-await]
tags: [asyncio, event-loop, gather, as-completed, httpx, to-thread, run-in-executor]
---

# The asyncio Event Loop and Downloading with HTTPX

## Core Idea

The **event loop** is the central scheduler in asyncio. It drives coroutines by calling `.send()` on them, suspends them when they `await` on I/O, and resumes them when results arrive. Your application code never interacts with the event loop directly in most cases -- you use high-level functions that schedule and coordinate coroutines.

The chapter demonstrates this by building concurrent HTTP downloaders using `httpx.AsyncClient`, progressing from simple to production-quality patterns.

## Key Event Loop Functions

| Function | What it does |
|---|---|
| `asyncio.run(coro)` | Create an event loop, run the coroutine to completion, close the loop. The standard entry point from sync to async. |
| `asyncio.gather(*awaitables)` | Run multiple awaitables concurrently. Returns a list of results **in submission order**. |
| `asyncio.as_completed(awaitables)` | Returns an iterator of awaitables that yield results **in completion order**. Ideal for progress bars. |
| `asyncio.create_task(coro)` | Schedule a coroutine to run concurrently. Returns a `Task` object. |
| `asyncio.to_thread(fn, *args)` | Run a blocking function in a thread (Python 3.9+). Returns an awaitable. |
| `loop.run_in_executor(executor, fn, *args)` | Older API for delegating to a thread or process pool. |

## The Basic Download Pattern

The simplest asyncio downloader uses `gather` to run all downloads concurrently:

```python
async def supervisor(cc_list: list[str]) -> int:
    async with httpx.AsyncClient() as client:
        to_do = [download_one(client, cc) for cc in sorted(cc_list)]
        res = await asyncio.gather(*to_do)
    return len(res)

def download_many(cc_list: list[str]) -> int:
    return asyncio.run(supervisor(cc_list))
```

Key observations:
- `download_many` is a **plain function** (the sync entry point), calling `asyncio.run()`.
- `httpx.AsyncClient` is an **async context manager**, managing connection pooling.
- A list comprehension creates coroutine objects; `gather` schedules them all at once.
- Results come back in the order tasks were submitted, not completion order.

## Processing Results as They Arrive

For progress bars or streaming results, use `asyncio.as_completed`:

```python
async def supervisor(cc_list, concur_req):
    semaphore = asyncio.Semaphore(concur_req)
    async with httpx.AsyncClient() as client:
        to_do = [download_one(client, cc, semaphore) for cc in cc_list]
        for coro in asyncio.as_completed(to_do):
            status = await coro  # won't block -- coro is already done
            update_progress_bar(status)
```

Unlike `gather`, `as_completed` yields coroutines in the order they **finish**. The `await` on each returned coroutine is instantaneous because the work is already complete.

## Delegating Blocking I/O to Threads

Not all I/O has an async API. File I/O, for example, is blocking in Python's standard library. The solution is to run it in a thread:

```python
# Python 3.9+ (preferred)
await asyncio.to_thread(save_flag, image, f'{cc}.gif')

# Python 3.7-3.8 equivalent
loop = asyncio.get_running_loop()
await loop.run_in_executor(None, save_flag, image, f'{cc}.gif')
```

Passing `None` as the executor uses the default `ThreadPoolExecutor`. For CPU-bound work, pass a `ProcessPoolExecutor` instance instead.

**Warning from Caleb Hattingh:** `run_in_executor` creates threads that are not truly cancellable. If you cancel the wrapping coroutine, the underlying thread keeps running. This can prevent clean shutdown of your asyncio program. Hattingh suggests mentally renaming it `run_in_executor_uncancellable`.

## Making Multiple Requests per Task

The `await` keyword eliminates the "pyramid of doom" (nested callbacks) when you need sequential async operations:

```python
async def download_one(client, cc, semaphore):
    async with semaphore:
        image = await get_flag(client, cc)      # first request
    async with semaphore:
        country = await get_country(client, cc)  # second request
    filename = country.replace(' ', '_')
    await asyncio.to_thread(save_flag, image, f'{filename}.gif')
```

Each `await` suspends the coroutine and yields control, but local variables (`image`, `country`) are preserved across suspension points. This is the key advantage over callback-based async: you keep the sequential logic and shared local scope.

## Practical Tips

1. **Hold semaphores for the shortest time possible.** Release before doing file I/O.
2. **Use `asyncio.gather` when you need all results.** Use `as_completed` when you need streaming progress.
3. **Always set `return_exceptions=True`** on `gather` in production code, so one failure does not cancel the rest.
4. **Respect servers**: throttle concurrent requests with a semaphore. Even with async, you can easily send hundreds of requests per second.

## See Also

- [[native-coroutines-and-async-await]] -- async/await fundamentals
- [[semaphores-for-throttling]] -- controlling concurrency with semaphores
- [[async-context-managers]] -- the `async with` pattern used with AsyncClient
