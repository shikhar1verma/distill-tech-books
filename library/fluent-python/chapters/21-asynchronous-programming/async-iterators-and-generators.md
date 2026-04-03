---
title: "Async Iterators, Generators, and Comprehensions"
slug: async-iterators-and-generators
chapter: 21
book: fluent-python
type: concept
depends_on: [native-coroutines-and-async-await]
tags: [async-for, async-iterator, async-generator, async-comprehension, anext, aiter]
---

# Async Iterators, Generators, and Comprehensions

## Core Idea

Just as `for` works with iterables (objects with `__iter__`/`__next__`), `async for` works with **asynchronous iterables** -- objects that implement `__aiter__` and `__anext__`. The key difference: `__anext__` is a **coroutine method**, so each step of iteration can yield to the event loop. This is essential for iterating over results that arrive asynchronously -- database cursor rows, streaming API responses, or DNS probe results.

**Async generator functions** (`async def` + `yield`) are the simplest way to create async iterables, just as generator functions simplify the classic Iterator pattern.

## The Async Iteration Protocol

| Method | Description | Is coroutine? |
|---|---|---|
| `__aiter__(self)` | Return the async iterator (usually `self`) | **No** -- regular method |
| `__anext__(self)` | Return the next item (raise `StopAsyncIteration` when done) | **Yes** -- coroutine |

An example from the `aiopg` PostgreSQL driver shows the real-world motivation:

```python
async def go():
    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1")
            async for row in cur:
                print(row)
```

The cursor might need to fetch additional batches of rows from the database. By implementing `__anext__` as a coroutine, the driver can yield to the event loop while waiting for more data, rather than blocking the entire program.

## Async Generator Functions

An async generator function is declared with `async def` and uses `yield` in its body. It returns an **async generator object** that implements the async iteration protocol automatically.

The book's `multi_probe` example demonstrates this pattern:

```python
async def multi_probe(domains: Iterable[str]) -> AsyncIterator[Result]:
    loop = asyncio.get_running_loop()
    coros = [probe(domain, loop) for domain in domains]
    for coro in asyncio.as_completed(coros):
        result = await coro
        yield result
```

Key observations:
- `asyncio.as_completed` is a **classic generator** (iterated with plain `for`), not an async one.
- `await coro` suspends until the DNS result arrives.
- `yield result` makes this function an async generator, producing results one at a time.
- The shorthand `yield await coro` works because Python parses it as `yield (await coro)`.

Consumers drive it with `async for`:

```python
async for domain, found in multi_probe(domains):
    print(f"{'+' if found else ' '} {domain}")
```

## Async Generators vs. Native Coroutines

These two kinds of `async def` functions are fundamentally different:

| | Native coroutine | Async generator |
|---|---|---|
| Contains `yield`? | No | Yes |
| Return value | Single value via `return` | Multiple values via `yield`; only empty `return` |
| Driven by | `await` expression | `async for` statement |
| Is awaitable? | Yes | No |
| Object type | `coroutine` | `async_generator` |

```python
>>> probe('python.org')
<coroutine object probe at 0x10e313740>

>>> multi_probe(names)
<async_generator object multi_probe at 0x10e246b80>

>>> for r in multi_probe(names):  # ERROR
TypeError: 'async_generator' object is not iterable
```

You cannot use a regular `for` loop with async generators -- they implement `__aiter__`, not `__iter__`.

## Async Comprehensions (PEP 530)

Python 3.6 added `async for` and `await` inside comprehensions and generator expressions.

### Async generator expression

```python
# Can be defined anywhere, but consumed only inside async def
gen_found = (name async for name, found in multi_probe(names) if found)
async for name in gen_found:
    print(name)
```

### Async list comprehension

```python
results = [result async for result in multi_probe(names)]
```

### Await in comprehension

```python
# Using await is similar to asyncio.gather, but sequential per await
results = [await probe(name) for name in names]
```

Note: using `await` in a list comprehension probes domains one at a time. For true concurrency, use `asyncio.gather`:

```python
results = await asyncio.gather(*[probe(name) for name in names])
```

### Dict and set comprehensions

```python
# Dict comprehension with async for
domain_map = {name: found async for name, found in multi_probe(names)}

# Set comprehension with await and filtering
found_set = {name for name in names if (await probe(name)).found}
```

All comprehensions with `async for` or `await` (except async generator expressions defined at module level) can only appear inside an `async def` body or the magic async console (`python -m asyncio`).

## The Async Console

Since Python 3.8, `python -m asyncio` launches an "async REPL" where you can use `await`, `async for`, and `async with` at the top-level prompt. This is invaluable for experimenting with async code:

```
$ python -m asyncio
>>> import asyncio
>>> await asyncio.sleep(1, 'wake up!')
'wake up!'
```

## See Also

- [[native-coroutines-and-async-await]] -- the `await` keyword that async generators use
- [[async-context-managers]] -- async generators used with `@asynccontextmanager`
- [[asyncio-event-loop-and-http]] -- `as_completed` used inside async generators
