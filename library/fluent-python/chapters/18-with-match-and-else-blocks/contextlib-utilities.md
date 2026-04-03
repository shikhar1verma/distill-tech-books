---
title: "The contextlib Utilities"
aliases: ["contextlib", "ExitStack", "suppress", "closing", "nullcontext"]
tags: [fluent-python, chapter-18, contextlib, context-manager]
chapter: 18
concept: 2
type: mixed
---

# The `contextlib` Utilities

## Core Idea

Before writing a custom context manager class, check `contextlib`. It provides ready-made utilities for common patterns, reducing boilerplate significantly.

## Utility Reference

### `closing(thing)`

Wraps an object that has a `.close()` method but does not implement `__enter__`/`__exit__`. Calls `thing.close()` on exit.

```python
from contextlib import closing
from urllib.request import urlopen

with closing(urlopen('https://example.com')) as page:
    content = page.read()
```

### `suppress(*exceptions)`

Silently ignores the specified exception types if they occur inside the block.

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove('nonexistent.tmp')
# No crash even if file doesn't exist
```

### `nullcontext(enter_result=None)`

A no-op context manager. Useful for conditional CM logic where you may or may not need an actual CM.

```python
from contextlib import nullcontext

cm = some_lock if thread_safe else nullcontext()
with cm:
    do_work()
```

### `redirect_stdout(new_target)` / `redirect_stderr(new_target)`

Temporarily redirects `sys.stdout` (or `sys.stderr`) to a file-like object.

```python
import io
from contextlib import redirect_stdout

buf = io.StringIO()
with redirect_stdout(buf):
    print('captured')
assert buf.getvalue() == 'captured\n'
```

### `ExitStack`

Manages a **dynamic number** of context managers. CMs are exited in LIFO order (last entered, first exited). Essential when you don't know at coding time how many CMs you need.

```python
from contextlib import ExitStack

with ExitStack() as stack:
    files = [stack.enter_context(open(f)) for f in file_paths]
    # All files are open; all will be closed on exit
```

### `AbstractContextManager`

An ABC that formalizes the CM interface. Provides a default `__enter__` that returns `self`; you only need to implement `__exit__`.

### `ContextDecorator`

A base class for CMs that can also be used as **function decorators**. The entire decorated function runs within the managed context.

### Async Variants (Python 3.7+)

- `AbstractAsyncContextManager`
- `@asynccontextmanager`
- `AsyncExitStack`

These mirror their sync counterparts but work with `async with`.

## Connections

- [[context-managers-and-with]] -- the underlying protocol these utilities build on
- [[contextmanager-decorator]] -- the most widely used contextlib utility, covered in depth
