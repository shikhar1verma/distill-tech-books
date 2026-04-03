---
title: "Spinner Example: Threads, Processes, and asyncio"
slug: spinner-example
chapter: 19
book: "Fluent Python"
type: code-heavy
depends_on:
  - threads-processes-coroutines
  - the-gil
tags: [threading, multiprocessing, asyncio, Event, Task]
---

# Spinner Example: Threads, Processes, and asyncio

## The Problem

Animate a text spinner (`\|/-`) while a slow computation runs for 3 seconds, then display the result. This simple task illustrates all three concurrency models.

## Version 1: Threading

```python
import itertools
import time
from threading import Thread, Event

def spin(msg: str, done: Event) -> None:
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)
        if done.wait(0.1):  # blocks up to 0.1s; True when event set
            break
    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')

def slow() -> int:
    time.sleep(3)  # releases the GIL
    return 42

def supervisor() -> int:
    done = Event()
    spinner = Thread(target=spin, args=('thinking!', done))
    spinner.start()
    result = slow()   # main thread blocks here
    done.set()        # signal spinner to stop
    spinner.join()    # wait for spinner thread
    return result
```

Key points:
- `threading.Event` coordinates shutdown. `done.wait(0.1)` serves double duty: it paces the animation at 10 FPS and checks the stop signal.
- `time.sleep()` releases the GIL, so the spinner thread runs freely.
- There is no API to kill a thread; we must send a signal (`done.set()`).

## Version 2: Multiprocessing

```python
from multiprocessing import Process, Event as MPEvent
from multiprocessing import synchronize

def spin(msg: str, done: synchronize.Event) -> None:
    # identical body to threading version
    ...

def supervisor() -> int:
    done = MPEvent()
    spinner = Process(target=spin, args=('thinking!', done))
    spinner.start()
    result = slow()
    done.set()
    spinner.join()
    return result
```

The API mirrors `threading` almost exactly. Differences:
- `multiprocessing.Event` is a *function* returning `synchronize.Event` (affects type hints).
- The spinner runs in a **separate Python process** with its own GIL.
- Data crossing process boundaries must be serializable. Here only the `Event` state crosses (implemented as an OS semaphore in C).

## Version 3: asyncio

```python
import asyncio
import itertools

async def spin(msg: str) -> None:
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, flush=True, end='')
        try:
            await asyncio.sleep(0.1)  # yields to event loop
        except asyncio.CancelledError:
            break
    blanks = ' ' * len(status)
    print(f'\r{blanks}\r', end='')

async def slow() -> int:
    await asyncio.sleep(3)  # NOT time.sleep!
    return 42

async def supervisor() -> int:
    spinner = asyncio.create_task(spin('thinking!'))
    result = await slow()
    spinner.cancel()  # raises CancelledError in spin
    return result

def main():
    result = asyncio.run(supervisor())
    print(f'Answer: {result}')
```

Key points:
- No `Event` needed -- `Task.cancel()` raises `CancelledError` at the `await` point.
- `asyncio.create_task()` schedules the coroutine; it starts running when the current coroutine yields.
- Using `time.sleep()` instead of `await asyncio.sleep()` would **freeze the spinner** because the event loop is blocked.

## The Critical Experiment

Replace `await asyncio.sleep(3)` with `time.sleep(3)` in the asyncio version:

1. The spinner task is created but never gets CPU time.
2. The program hangs for 3 seconds.
3. The spinner is cancelled before it runs even once.

**Lesson:** Never use `time.sleep()` in asyncio coroutines. Use `await asyncio.sleep()`.

## Supervisors Compared

| Aspect | threading | asyncio |
|---|---|---|
| Start background work | `Thread(target=fn).start()` | `asyncio.create_task(coro())` |
| Signal stop | `Event.set()` | `Task.cancel()` |
| Wait for cleanup | `thread.join()` | Automatic (cancel at `await`) |
| Data safety | Needs locks | Safe by default (one coro at a time) |
| Scheduling | Preemptive (OS) | Cooperative (`await` = yield point) |

## CPU-Bound Quick Quiz

What happens to the spinner if `time.sleep(3)` becomes `is_prime(big_number)`?

- **multiprocessing**: spinner keeps spinning (separate process).
- **threading**: spinner keeps spinning (GIL releases every 5ms; spinner needs very little CPU).
- **asyncio**: spinner freezes completely (`is_prime` never yields with `await`).

The threading answer surprises many people. The GIL's 5ms switch interval is enough for the lightweight spinner, which only needs a microsecond per frame.
