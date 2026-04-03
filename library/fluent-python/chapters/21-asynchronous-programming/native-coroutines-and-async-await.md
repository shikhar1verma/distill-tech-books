---
title: "Native Coroutines and async/await"
slug: native-coroutines-and-async-await
chapter: 21
book: fluent-python
type: concept
depends_on: []
tags: [async, await, coroutines, asyncio, event-loop, awaitable]
---

# Native Coroutines and `async`/`await`

## Core Idea

A **native coroutine** is a function defined with `async def`. It is driven by the `await` keyword, which suspends the coroutine and yields control back to the event loop. Under the hood, the event loop calls `.send()` on the coroutine object -- the same mechanism that powers classic generators -- but you never see those calls in application code. The `await` keyword borrows most of its implementation from `yield from`, which also makes `.send()` calls to drive coroutines through a chain of delegation.

When you call an `async def` function, it does **not** execute the body. Instead, it returns a **coroutine object** -- an awaitable that must be driven by `asyncio.run()`, `await`, or one of the scheduling functions like `asyncio.gather()` or `asyncio.create_task()`.

## Guido's Trick to Read Async Code

Guido van Rossum suggested a simple mental model: **squint and pretend the `async` and `await` keywords are not there.** What remains reads like a plain sequential function -- except it magically never blocks. For example:

```python
async def probe(domain: str) -> tuple[str, bool]:
    loop = asyncio.get_running_loop()
    try:
        await loop.getaddrinfo(domain, None)
    except socket.gaierror:
        return (domain, False)
    return (domain, True)
```

Remove `async` and `await` and you get a normal function that calls `getaddrinfo`, catches an exception, and returns a tuple. The `await` is what makes the call non-blocking: it suspends `probe` while the DNS query is in flight, letting the event loop drive other coroutines in the meantime.

## Awaitables

The `for` keyword works with *iterables*. The `await` keyword works with *awaitables*. As an end user of asyncio, the awaitables you encounter daily are:

- **Native coroutine objects** -- returned by calling an `async def` function.
- **`asyncio.Task` objects** -- created by `asyncio.create_task()`, which wraps a coroutine and schedules it for concurrent execution.
- **Objects with `__await__`** -- including `asyncio.Future` (lower-level, mostly for library authors).

You use `await other_coro()` when you need the result right now. You use `asyncio.create_task(one_coro())` when you want to schedule work without waiting for it.

## The Secret: Humble Generators

The `await` chain in your code eventually reaches a low-level awaitable deep inside asyncio or a library like HTTPX. That low-level awaitable returns a generator that the event loop can drive in response to I/O events or timers. Your coroutines sit in the middle: asyncio drives them with `.send()`, and they drive library coroutines with `await`, forming a channel between the event loop and the I/O library.

```
Event loop  -->  .send()  -->  your coroutine  -->  await  -->  library coroutine
                                                                      |
                                                            low-level generator
                                                            (responds to I/O events)
```

Using functions like `asyncio.gather` and `asyncio.create_task`, you start multiple concurrent `await` chains, enabling concurrent I/O operations in a single thread.

## The All-or-Nothing Problem

This is the defining constraint of async programming: **once you go async, every function that does I/O must be async too**, or delegated to a thread. You cannot reuse a blocking function like `requests.get()` inside a coroutine without wrapping it in `asyncio.to_thread()` or `loop.run_in_executor()`.

As the chapter's epigraph puts it: "You rewrite all your code so none of it blocks or you're just wasting your time." This is why the book had to rewrite `get_flag` as a coroutine using `httpx.AsyncClient` rather than reusing the synchronous version.

## Practical Patterns

```python
import asyncio

# Pattern 1: asyncio.run() as the single sync-to-async bridge
async def main():
    result = await some_coroutine()
    print(result)

asyncio.run(main())  # blocks until main() completes

# Pattern 2: create_task for fire-and-forget concurrency
async def supervisor():
    spinner_task = asyncio.create_task(spin())  # runs concurrently
    result = await slow_computation()           # blocks this coroutine only
    spinner_task.cancel()
    return result
```

## See Also

- [[asyncio-event-loop-and-http]] -- event loop, gather, and as_completed in depth
- [[async-vs-threads-and-pitfalls]] -- when async helps and when it hurts
- [[async-context-managers]] -- the `async with` statement
