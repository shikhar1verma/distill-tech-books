---
title: "Asynchronous Context Managers"
slug: async-context-managers
chapter: 21
book: fluent-python
type: concept
depends_on: [native-coroutines-and-async-await]
tags: [async-with, context-manager, aenter, aexit, asynccontextmanager]
---

# Asynchronous Context Managers

## Core Idea

The `async with` statement works with objects that implement `__aenter__` and `__aexit__` as **coroutine methods**. This is necessary when the setup and teardown of a resource involve asynchronous operations -- network connections, database transactions, acquiring async locks -- that must yield to the event loop rather than block.

The relationship mirrors the synchronous world: `with` uses `__enter__`/`__exit__`, while `async with` uses `__aenter__`/`__aexit__`. PEP 492 introduced this alongside `async def` and `await` in Python 3.5.

## The Protocol

An asynchronous context manager must provide two coroutine methods:

```python
class AsyncContextManager:
    async def __aenter__(self):
        # async setup -- e.g., open connection, start transaction
        return self  # or some resource

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # async teardown -- e.g., commit/rollback, close connection
        return False  # True to suppress exception
```

Used as:

```python
async with AsyncContextManager() as resource:
    await resource.do_something()
```

## Real-World Examples

### HTTP Client Sessions

The `httpx.AsyncClient` is an async context manager that manages connection pooling:

```python
async with httpx.AsyncClient() as client:
    resp = await client.get(url)
```

The `__aenter__` method sets up the connection pool, and `__aexit__` closes all connections gracefully.

### Database Transactions

The `asyncpg` PostgreSQL driver uses async context managers for transactions. Without `async with`:

```python
tr = connection.transaction()
await tr.start()
try:
    await connection.execute("INSERT INTO mytable VALUES (1, 2, 3)")
except:
    await tr.rollback()
    raise
else:
    await tr.commit()
```

With `async with`:

```python
async with connection.transaction():
    await connection.execute("INSERT INTO mytable VALUES (1, 2, 3)")
```

The `Transaction.__aenter__` calls `await self.start()`, and `__aexit__` awaits on `commit` or `rollback` depending on whether an exception occurred. Because both setup and teardown are coroutines, asyncpg can handle many transactions concurrently without blocking.

### Semaphores

`asyncio.Semaphore` is also an async context manager. Its `__aenter__` awaits `.acquire()` (which may suspend if the counter is zero), and `__aexit__` calls `.release()`:

```python
async with semaphore:
    image = await get_flag(client, cc)
```

## The `@asynccontextmanager` Decorator

Just as `@contextmanager` from `contextlib` lets you write sync context managers with a generator function, `@asynccontextmanager` (added in Python 3.7) lets you write async context managers with an **async generator function**:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def web_page(url):
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, download_webpage, url)
    yield data  # <-- everything before yield is __aenter__
    await loop.run_in_executor(None, update_stats, url)
    # <-- everything after yield is __aexit__
```

Usage:

```python
async with web_page('google.com') as data:
    process(data)
```

This pattern is especially useful when:
- The setup and teardown are simple (a few lines each).
- You want to avoid writing a full class with `__aenter__`/`__aexit__`.
- You need to delegate blocking calls to a thread executor.

The value yielded becomes the target of the `as` clause. Error handling at the `yield` line works the same as with the synchronous `@contextmanager` -- wrap `yield` in `try/finally` to guarantee cleanup.

## When to Use `async with`

Use `async with` whenever a resource requires **asynchronous setup or teardown**:

| Resource | Library | Why async? |
|---|---|---|
| HTTP session | httpx, aiohttp | Connection pool management |
| DB transaction | asyncpg, databases | Network-based commit/rollback |
| Semaphore/Lock | asyncio | May need to suspend until available |
| File handle | aiofiles | Async filesystem operations |
| WebSocket | websockets | Network handshake |

If setup and teardown are purely CPU-bound and instantaneous, a regular `with` statement is fine -- no need for `async with`.

## See Also

- [[native-coroutines-and-async-await]] -- the `await` keyword that powers async context managers
- [[semaphores-for-throttling]] -- semaphores as async context managers
- [[async-iterators-and-generators]] -- async generators used with `@asynccontextmanager`
