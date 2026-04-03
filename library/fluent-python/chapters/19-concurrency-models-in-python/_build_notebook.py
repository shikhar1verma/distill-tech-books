#!/usr/bin/env python3
"""Generate the Chapter 19 interactive notebook."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "src"))
from notebook_builder import build_notebook

TITLE = "Chapter 19: Concurrency Models in Python"

cells = [
    # ── Title ──
    {"type": "markdown", "content": (
        "# Chapter 19 -- Concurrency Models in Python\n"
        "*Fluent Python, 2nd Edition -- Luciano Ramalho*\n\n"
        "This notebook distills the key ideas from Chapter 19 into runnable code.\n"
        "Topics: concurrency vs parallelism, threads, processes, coroutines, the GIL, "
        "process pools, and Python's multicore ecosystem."
    )},

    # ── 1. Concurrency vs Parallelism ──
    {"type": "markdown", "content": (
        "---\n"
        "## 1. Concurrency vs Parallelism\n\n"
        "> *Concurrency is about dealing with lots of things at once.*\n"
        "> *Parallelism is about doing lots of things at once.* -- Rob Pike\n\n"
        "- **Concurrency** = structure that handles multiple pending tasks (may interleave on 1 core).\n"
        "- **Parallelism** = simultaneous execution (requires multiple cores/CPUs).\n"
        "- All parallel systems are concurrent, but not all concurrent systems are parallel."
    )},
    {"type": "code", "content": (
        "import os\n"
        "print(f'CPU cores available: {os.cpu_count()}')\n"
        "print('A modern OS runs hundreds of processes concurrently on these few cores.')"
    )},

    # ── 2. Execution Units ──
    {"type": "markdown", "content": (
        "---\n"
        "## 2. Execution Units: Processes, Threads, and Coroutines\n\n"
        "| Feature | Process | Thread | Coroutine |\n"
        "|---|---|---|---|\n"
        "| Memory | Isolated (own space) | Shared (same process) | Shared (same thread) |\n"
        "| Scheduling | Preemptive (OS) | Preemptive (OS) | Cooperative (`await`) |\n"
        "| Startup cost | High | Medium | Very low |\n"
        "| CPU parallelism | Yes | No (GIL) | No |\n"
        "| Best for | CPU-bound work | I/O-bound work | I/O-bound + high concurrency |"
    )},

    # ── 3. The GIL ──
    {"type": "markdown", "content": (
        "---\n"
        "## 3. The Global Interpreter Lock (GIL)\n\n"
        "Key points about the GIL in CPython:\n"
        "1. Only **one thread** can execute Python bytecode at any time.\n"
        "2. The GIL is released every ~5ms (`sys.getswitchinterval()`).\n"
        "3. The GIL is released during **all syscalls** (disk I/O, network I/O, `time.sleep`).\n"
        "4. C extensions (NumPy, zlib) can release the GIL while doing heavy work.\n"
        "5. For CPU-bound parallelism, use **multiprocessing** (separate GILs per process)."
    )},
    {"type": "code", "content": (
        "import sys\n"
        "print(f'GIL switch interval: {sys.getswitchinterval():.4f}s')\n"
        "print('The interpreter pauses the running thread every ~5ms to let others run.')"
    )},

    # ── 4. Spinner with Threads ──
    {"type": "markdown", "content": (
        "---\n"
        "## 4. Spinner with Threads\n\n"
        "The classic concurrent \"Hello World\": animate a spinner in one thread while a\n"
        "slow computation runs in another. `threading.Event` coordinates shutdown."
    )},
    {"type": "code", "content": (
        "import itertools\n"
        "import time\n"
        "from threading import Thread, Event\n\n"
        "def spin_thread(msg: str, done: Event) -> None:\n"
        "    \"\"\"Animate a spinner until `done` is set.\"\"\"\n"
        "    status = ''\n"
        "    for char in itertools.cycle(r'\\|/-'):\n"
        "        status = f'\\r{char} {msg}'\n"
        "        print(status, end='', flush=True)\n"
        "        if done.wait(0.1):   # blocks up to 0.1s; returns True when event is set\n"
        "            break\n"
        "    blanks = ' ' * len(status)\n"
        "    print(f'\\r{blanks}\\r', end='')\n\n"
        "def slow_thread() -> int:\n"
        "    \"\"\"Simulate a slow computation. sleep() releases the GIL.\"\"\"\n"
        "    time.sleep(1)  # shortened for notebook demo\n"
        "    return 42\n\n"
        "def supervisor_thread() -> int:\n"
        "    done = Event()\n"
        "    spinner = Thread(target=spin_thread, args=('thinking!', done))\n"
        "    print(f'spinner object: {spinner}')\n"
        "    spinner.start()\n"
        "    result = slow_thread()     # main thread blocks here\n"
        "    done.set()                 # signal the spinner to stop\n"
        "    spinner.join()             # wait for spinner thread to finish\n"
        "    return result\n\n"
        "answer = supervisor_thread()\n"
        "print(f'Answer: {answer}')"
    )},

    # ── 5. Spinner with Processes ──
    {"type": "markdown", "content": (
        "---\n"
        "## 5. Spinner with Processes\n\n"
        "`multiprocessing.Process` mirrors the `threading.Thread` API but runs in\n"
        "a **separate Python interpreter** (separate GIL). True parallelism on multiple cores.\n\n"
        "The code is nearly identical -- swap `Thread` for `Process` and\n"
        "`threading.Event` for `multiprocessing.Event`.\n\n"
        "```python\n"
        "from multiprocessing import Process, Event as MPEvent\n\n"
        "def supervisor_proc() -> int:\n"
        "    done = MPEvent()\n"
        "    spinner = Process(target=spin_thread, args=('thinking!', done))\n"
        "    spinner.start()\n"
        "    result = slow_thread()\n"
        "    done.set()\n"
        "    spinner.join()\n"
        "    return result\n"
        "```\n\n"
        "> Note: multiprocessing.Event is actually a *function* that returns a\n"
        "> `synchronize.Event` instance -- a subtle API difference revealed by type hints."
    )},

    # ── 6. Spinner with asyncio ──
    {"type": "markdown", "content": (
        "---\n"
        "## 6. Spinner with Coroutines (asyncio)\n\n"
        "All coroutines run in **one thread**, driven by an event loop.\n"
        "Three ways to run a coroutine:\n"
        "- `asyncio.run(coro())` -- entry point, blocks until done.\n"
        "- `asyncio.create_task(coro())` -- schedule for later, returns a `Task`.\n"
        "- `await coro()` -- suspend current coroutine, resume when `coro` finishes."
    )},
    {"type": "code", "content": (
        "import asyncio\n"
        "import itertools\n\n"
        "async def spin_async(msg: str) -> None:\n"
        "    for char in itertools.cycle(r'\\|/-'):\n"
        "        status = f'\\r{char} {msg}'\n"
        "        print(status, end='', flush=True)\n"
        "        try:\n"
        "            await asyncio.sleep(0.1)   # yields control to event loop\n"
        "        except asyncio.CancelledError:\n"
        "            break\n"
        "    blanks = ' ' * len(status)\n"
        "    print(f'\\r{blanks}\\r', end='')\n\n"
        "async def slow_async() -> int:\n"
        "    await asyncio.sleep(1)   # MUST use await asyncio.sleep, NOT time.sleep!\n"
        "    return 42\n\n"
        "async def supervisor_async() -> int:\n"
        "    spinner = asyncio.create_task(spin_async('thinking!'))\n"
        "    print(f'spinner object: {spinner}')\n"
        "    result = await slow_async()   # control goes to event loop -> spinner runs\n"
        "    spinner.cancel()              # raises CancelledError in spin_async\n"
        "    return result\n\n"
        "# In a notebook, the event loop is already running, so we use await directly.\n"
        "# In a script you would use: asyncio.run(supervisor_async())\n"
        "try:\n"
        "    import nest_asyncio\n"
        "    nest_asyncio.apply()\n"
        "    answer = asyncio.run(supervisor_async())\n"
        "except ImportError:\n"
        "    # Fallback: if nest_asyncio not installed, run with get_event_loop\n"
        "    loop = asyncio.new_event_loop()\n"
        "    answer = loop.run_until_complete(supervisor_async())\n"
        "    loop.close()\n"
        "print(f'Answer: {answer}')"
    )},

    # ── 7. Side-by-side comparison ──
    {"type": "markdown", "content": (
        "---\n"
        "## 7. Supervisors Side-by-Side\n\n"
        "| Aspect | `threading` | `asyncio` |\n"
        "|---|---|---|\n"
        "| Start work | `Thread(target=fn).start()` | `asyncio.create_task(coro())` |\n"
        "| Signal stop | `Event.set()` | `Task.cancel()` |\n"
        "| Wait for finish | `thread.join()` | (automatic after cancel) |\n"
        "| Interruption | Preemptive (OS decides) | Cooperative (`await` is the yield point) |\n"
        "| Safety | Must use locks for shared data | Protected by default; only one coro runs |\n\n"
        "Key insight: coroutines are \"synchronized\" by definition -- only one runs at a time.\n"
        "They can only be cancelled at an `await` point, so cleanup is straightforward."
    )},

    # ── 8. GIL Impact Quiz ──
    {"type": "markdown", "content": (
        "---\n"
        "## 8. The GIL Impact: CPU-Bound Quick Quiz\n\n"
        "What happens to the spinner if you replace `time.sleep(3)` with a CPU-intensive\n"
        "`is_prime(n)` call?\n\n"
        "| Model | Spinner behavior | Why |\n"
        "|---|---|---|\n"
        "| **multiprocessing** | Keeps spinning | Separate process, separate GIL |\n"
        "| **threading** | Keeps spinning (!) | GIL releases every 5ms; spinner needs very little CPU |\n"
        "| **asyncio** | Freezes completely | Single thread; `is_prime` never does `await`, so event loop is blocked |"
    )},
    {"type": "code", "content": (
        "import math\n\n"
        "def is_prime(n: int) -> bool:\n"
        "    \"\"\"Simple trial-division primality test.\"\"\"\n"
        "    if n < 2:\n"
        "        return False\n"
        "    if n == 2:\n"
        "        return True\n"
        "    if n % 2 == 0:\n"
        "        return False\n"
        "    root = math.isqrt(n)\n"
        "    for i in range(3, root + 1, 2):\n"
        "        if n % i == 0:\n"
        "            return False\n"
        "    return True\n\n"
        "# Quick test with small primes\n"
        "test_numbers = [2, 17, 97, 100, 7919, 1_000_000_007]\n"
        "for n in test_numbers:\n"
        "    print(f'is_prime({n:>13_}) = {is_prime(n)}')"
    )},

    # ── 9. Process Pool with Queues ──
    {"type": "markdown", "content": (
        "---\n"
        "## 9. Homegrown Process Pool with Queues\n\n"
        "Pattern for distributing CPU-bound work across cores:\n"
        "1. Create a **job queue** and a **result queue**.\n"
        "2. Fork N worker processes, each looping on `jobs.get()`.\n"
        "3. Workers put results in the result queue.\n"
        "4. Use a **poison pill** (sentinel value like `0`) to signal workers to exit.\n\n"
        "This is exactly what `concurrent.futures.ProcessPoolExecutor` does internally\n"
        "(Chapter 20)."
    )},
    {"type": "code", "content": (
        "from multiprocessing import Process, SimpleQueue, cpu_count\n"
        "from time import perf_counter\n"
        "from typing import NamedTuple\n\n"
        "class PrimeResult(NamedTuple):\n"
        "    n: int\n"
        "    prime: bool\n"
        "    elapsed: float\n\n"
        "def check(n: int) -> PrimeResult:\n"
        "    t0 = perf_counter()\n"
        "    prime = is_prime(n)\n"
        "    return PrimeResult(n, prime, perf_counter() - t0)\n\n"
        "def worker(jobs, results):\n"
        "    while (n := jobs.get()):   # 0 is the poison pill\n"
        "        results.put(check(n))\n"
        "    results.put(PrimeResult(0, False, 0.0))  # signal: this worker is done\n\n"
        "# Sample numbers to check\n"
        "NUMBERS = [\n"
        "    2, 142_702_110_479_723,\n"
        "    299_593_572_317_531, 3_333_333_333_333_301,\n"
        "    3_333_333_333_333_333, 4_444_444_444_444_423,\n"
        "    4_444_444_444_444_444, 5_555_555_555_555_503,\n"
        "    5_555_555_555_555_555, 9_999_999_999_999_917,\n"
        "]\n\n"
        "def main_procs(num_procs: int = 0) -> None:\n"
        "    procs = num_procs or cpu_count()\n"
        "    # Cap at number of jobs to avoid idle workers\n"
        "    procs = min(procs, len(NUMBERS))\n"
        "    print(f'Checking {len(NUMBERS)} numbers with {procs} processes:')\n"
        "    t0 = perf_counter()\n\n"
        "    jobs: SimpleQueue = SimpleQueue()\n"
        "    results: SimpleQueue = SimpleQueue()\n\n"
        "    # Enqueue jobs\n"
        "    for n in NUMBERS:\n"
        "        jobs.put(n)\n"
        "    # Enqueue poison pills\n"
        "    for _ in range(procs):\n"
        "        jobs.put(0)\n\n"
        "    # Start workers\n"
        "    workers = []\n"
        "    for _ in range(procs):\n"
        "        p = Process(target=worker, args=(jobs, results))\n"
        "        p.start()\n"
        "        workers.append(p)\n\n"
        "    # Collect results\n"
        "    checked = 0\n"
        "    procs_done = 0\n"
        "    while procs_done < procs:\n"
        "        n, prime, elapsed = results.get()\n"
        "        if n == 0:\n"
        "            procs_done += 1\n"
        "        else:\n"
        "            checked += 1\n"
        "            label = 'P' if prime else ' '\n"
        "            print(f'{n:>20_}  {label}  {elapsed:9.6f}s')\n\n"
        "    # Wait for all workers to finish\n"
        "    for p in workers:\n"
        "        p.join()\n\n"
        "    elapsed = perf_counter() - t0\n"
        "    print(f'{checked} checks in {elapsed:.2f}s')\n\n"
        "main_procs(4)"
    )},

    # ── 10. Threading is a non-solution for CPU-bound ──
    {"type": "markdown", "content": (
        "---\n"
        "## 10. Threading: A Non-Solution for CPU-Bound Work\n\n"
        "Due to the GIL, a threaded version of the prime checker is **slower** than\n"
        "sequential code, and gets worse as you add threads (context-switching overhead).\n\n"
        "**Rule of thumb:**\n"
        "- I/O-bound work --> threads or coroutines\n"
        "- CPU-bound work --> processes"
    )},
    {"type": "code", "content": (
        "# Sequential baseline for comparison\n"
        "SMALL_SAMPLE = [2, 142_702_110_479_723, 299_593_572_317_531, 3_333_333_333_333_333]\n\n"
        "t0 = perf_counter()\n"
        "for n in SMALL_SAMPLE:\n"
        "    result = check(n)\n"
        "    label = 'P' if result.prime else ' '\n"
        "    print(f'{n:>20_}  {label}  {result.elapsed:9.6f}s')\n"
        "print(f'Sequential total: {perf_counter() - t0:.2f}s')"
    )},

    # ── 11. Python Multicore Ecosystem ──
    {"type": "markdown", "content": (
        "---\n"
        "## 11. Python in the Multicore World\n\n"
        "Despite the GIL, Python thrives at scale through:\n\n"
        "### WSGI/ASGI Application Servers\n"
        "- **Gunicorn**, **uWSGI**, **NGINX Unit** fork multiple worker processes.\n"
        "- Each worker has its own GIL -- concurrency is transparent to app code.\n"
        "- ASGI (for async frameworks like **FastAPI**, **Starlette**) is the successor to WSGI.\n\n"
        "### Distributed Task Queues\n"
        "- **Celery** and **RQ** offload work to background processes, even on other machines.\n"
        "- Use Redis or RabbitMQ as message brokers.\n"
        "- Producer/consumer pattern -- the same idea as our `SimpleQueue` process pool.\n\n"
        "### Data Science Ecosystem\n"
        "- **NumPy**, **SciPy**, **Pandas** release the GIL in C/Fortran extensions.\n"
        "- **Dask** distributes work across local cores or entire clusters.\n"
        "- **TensorFlow** and **PyTorch** leverage GPUs and multi-node training."
    )},

    # ── 12. Key Takeaways ──
    {"type": "markdown", "content": (
        "---\n"
        "## 12. Key Takeaways\n\n"
        "1. **Concurrency != Parallelism.** Concurrency is structural; parallelism is about execution.\n"
        "2. **The GIL** prevents CPU parallelism with threads, but I/O-bound threads work fine.\n"
        "3. **Three models:** `threading` (preemptive, shared memory), `multiprocessing` (preemptive, isolated), `asyncio` (cooperative, single-threaded).\n"
        "4. **Never block the event loop** in asyncio -- use `await asyncio.sleep()`, not `time.sleep()`.\n"
        "5. **CPU-bound work** needs `multiprocessing` or `ProcessPoolExecutor`.\n"
        "6. **At scale,** WSGI servers, task queues, and the data-science ecosystem bypass the GIL transparently.\n"
        "7. **Queues and sentinels** are the fundamental coordination primitives for concurrent workers."
    )},
]

OUTPUT = os.path.join(os.path.dirname(__file__), "notebook.ipynb")
build_notebook(TITLE, cells, OUTPUT)
print(f"Notebook written to {OUTPUT}")
