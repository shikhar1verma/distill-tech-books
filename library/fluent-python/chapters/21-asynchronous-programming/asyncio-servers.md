---
title: "Writing asyncio Servers"
slug: asyncio-servers
chapter: 21
book: fluent-python
type: concept
depends_on: [native-coroutines-and-async-await, async-context-managers]
tags: [asyncio, server, fastapi, tcp, asgi, streamreader, streamwriter]
---

# Writing asyncio Servers

## Core Idea

The chapter demonstrates server-side asyncio through two examples: a **FastAPI web service** using the ASGI protocol and a **plain TCP server** using `asyncio.start_server()` with `StreamReader`/`StreamWriter`. Both serve a Unicode character search utility ("mojifinder"), showing how the same domain logic can be exposed through different protocols.

## A FastAPI Web Service

FastAPI is an ASGI web framework that leverages type hints, decorators, and pydantic for automatic validation and OpenAPI documentation. The complete `web_mojifinder.py` server fits in about 20 lines of Python:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title='Mojifinder Web')

class CharName(BaseModel):
    char: str
    name: str

@app.get('/search', response_model=list[CharName])
async def search(q: str):
    chars = sorted(app.state.index.search(q))
    return ({'char': c, 'name': name(c)} for c in chars)

@app.get('/', response_class=HTMLResponse)
def form():
    return app.state.form
```

Key points about FastAPI:

- **Coroutine or plain function:** both work as route handlers. FastAPI handles the difference internally. Use `async def` when the handler needs to `await` on async database or HTTP calls.
- **Parameter inference:** if `q` appears in the function signature but not in the URL path, FastAPI assumes it comes from the query string (`/search?q=cat`).
- **`response_model`:** declares the JSON schema using a pydantic model. You can return dicts or generators -- FastAPI validates and serializes them.
- **No `asyncio.run()`:** the ASGI server (uvicorn, hypercorn, or daphne) manages the event loop.

Run it with:

```bash
uvicorn web_mojifinder:app --reload
```

FastAPI auto-generates interactive API documentation at `/docs` (Swagger UI).

## An asyncio TCP Server

For low-level protocol handling, `asyncio.start_server()` creates a TCP server. You provide a callback (function or coroutine) that receives a `StreamReader` and `StreamWriter` for each client connection:

```python
async def supervisor(index, host, port):
    server = await asyncio.start_server(
        functools.partial(finder, index),
        host, port,
    )
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}. Hit CTRL-C to stop.')
    await server.serve_forever()
```

The `finder` coroutine handles one client session in a loop:

```python
async def finder(index, reader, writer):
    client = writer.get_extra_info('peername')
    while True:
        writer.write(PROMPT)       # plain function -- writes to buffer
        await writer.drain()        # coroutine -- flushes buffer to network
        data = await reader.readline()  # coroutine -- reads from network
        if not data:
            break
        query = data.decode().strip()
        if ord(query[:1]) < 32:
            break
        results = await search(query, index, writer)
    writer.close()
    await writer.wait_closed()
```

### The StreamWriter API Gotcha

`StreamWriter` mixes plain methods and coroutines in ways that can be confusing:

| Method | Type | Notes |
|---|---|---|
| `writer.write(data)` | Plain function | Writes to buffer, does not do network I/O |
| `writer.writelines(data)` | Plain function | Same, but accepts an iterable |
| `writer.drain()` | **Coroutine** | Flushes buffer to network -- must `await` |
| `writer.close()` | Plain function | Initiates close |
| `writer.wait_closed()` | **Coroutine** | Waits for close to complete -- must `await` |

Similarly, `reader.readline()` and `reader.read()` are coroutines.

The documentation now clearly labels which methods are coroutines, but this mixed API remains a source of bugs for newcomers.

## How the TCP Server Handles Concurrency

Each client connection spawns a new `finder` coroutine. When one coroutine is suspended at `await reader.readline()` (waiting for user input), the event loop drives other coroutine instances for other connected clients. This achieves concurrency without threads:

```
Client A: await reader.readline() -- suspended
Client B: writer.write(response) -- active
Client C: await reader.readline() -- suspended
```

The `server.serve_forever()` call keeps the event loop alive. `supervisor` is suspended at that line until a `KeyboardInterrupt` or cancellation.

## functools.partial for Callback Adaptation

`asyncio.start_server` expects a callback with exactly two parameters: `reader` and `writer`. When your handler needs additional context (like the search index), use `functools.partial`:

```python
callback = functools.partial(finder, index)
# callback(reader, writer) calls finder(index, reader, writer)
```

This is the most common use case for `functools.partial` in asyncio programs.

## ASGI vs. Raw TCP

| | FastAPI (ASGI) | asyncio TCP |
|---|---|---|
| Protocol | HTTP | Raw TCP |
| Dependencies | fastapi, uvicorn | Standard library only |
| Routing | Decorators | Manual parsing |
| Serialization | Automatic (pydantic) | Manual encode/decode |
| Best for | Web APIs, SPAs | Custom protocols, low-level networking |

For most web applications, ASGI frameworks (FastAPI, Starlette, Litestar) are the right choice. Raw TCP servers are for specialized protocols or educational purposes.

## See Also

- [[native-coroutines-and-async-await]] -- the coroutines that power server handlers
- [[async-context-managers]] -- used by the HTTP client and database examples
- [[async-vs-threads-and-pitfalls]] -- why async servers excel at I/O-bound workloads
