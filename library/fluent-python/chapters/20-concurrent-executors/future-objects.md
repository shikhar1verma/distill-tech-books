---
title: "Future Objects: submit, result, as_completed"
slug: future-objects
chapter: 20
book: fluent-python
type: code-heavy
depends_on:
  - thread-pool-executor
tags: [concurrency, futures, as-completed, submit, callback]
---

# Future Objects: `submit`, `result`, `as_completed`

## Core Idea

A **Future** represents a deferred computation that may or may not have completed. You never create Futures directly -- the executor creates them when you call `submit()`. The concurrency framework manages their lifecycle.

Python has two Future classes:
- `concurrent.futures.Future` -- used with thread/process pools
- `asyncio.Future` -- used with the async event loop

Both serve the same purpose but differ in how `result()` behaves when the future is not yet done.

## The Future API

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=3) as executor:
    future = executor.submit(some_function, arg1, arg2)

    future.done()         # Non-blocking: True if callable has finished
    future.result()       # Blocks until result is ready (or raises exception)
    future.result(timeout=5)  # Raises TimeoutError if not done in 5s
    future.add_done_callback(fn)  # fn(future) called when future completes
```

## `submit` + `as_completed` Pattern

When you need results **as they finish** (not in submission order), use `submit()` with `as_completed()`:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=3) as executor:
    to_do: list[futures.Future] = []
    for cc in sorted(cc_list):
        future = executor.submit(download_one, cc)
        to_do.append(future)

    for future in as_completed(to_do):
        result = future.result()  # won't block -- future is already done
        print(result)
```

`as_completed` yields futures as they finish, so you can process fast results immediately rather than waiting for slow ones.

## Future States

A future transitions through these states:

```
PENDING  -->  RUNNING  -->  FINISHED
```

The book shows this with `repr()` output:

```
Scheduled for BR: <Future at 0x... state=running>
Scheduled for IN: <Future at 0x... state=pending>
...
<Future at 0x... state=finished returned str> result: 'BR'
```

With `max_workers=3` and 5 tasks, the first 3 are `running` and the last 2 are `pending`, waiting for a free worker thread.

## `executor.map` vs `submit` + `as_completed`

| Feature | `executor.map` | `submit` + `as_completed` |
|---|---|---|
| Result order | submission order | completion order |
| Callable flexibility | same callable for all items | different callables per task |
| Error handling | exception on iteration | exception via `future.result()` |
| Progress display | harder (blocked on order) | easier (process as they arrive) |
| Multiple executors | no | yes -- futures from different executors |

The combination of `submit` + `as_completed` is more flexible: you can submit different callables with different arguments, and the futures you pass to `as_completed` can even come from different executor instances.

## See Also

- [[thread-pool-executor]] -- `executor.map` for simpler cases
- [[error-handling-concurrent]] -- Error handling patterns with `as_completed`
- [[executor-map-behavior]] -- Why `map` results block in order
