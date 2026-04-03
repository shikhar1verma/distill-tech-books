---
title: "Concurrency vs Parallelism: The Big Picture"
slug: concurrency-vs-parallelism
chapter: 19
book: "Fluent Python"
type: theory-heavy
depends_on: []
tags: [concurrency, parallelism, fundamentals]
---

# Concurrency vs Parallelism: The Big Picture

## Core Distinction

Rob Pike (co-inventor of Go) draws a clean line:

- **Concurrency** is about *dealing with* lots of things at once -- it is a matter of **structure**.
- **Parallelism** is about *doing* lots of things at once -- it is a matter of **execution**.

All parallel systems are concurrent, but not all concurrent systems are parallel. A single-core CPU can run hundreds of processes concurrently by interleaving their execution; it cannot run any of them in parallel.

## Why It Matters for Python

A modern laptop with 4-6 cores routinely manages 200+ processes. The OS scheduler gives each process periodic CPU time, creating the illusion of simultaneous progress. True parallelism -- multiple computations executing at the same instant -- requires multiple cores.

Python supports both concurrency and parallelism:

| Approach | Concurrent | Parallel | Package |
|---|---|---|---|
| Threads | Yes | No (GIL) | `threading` |
| Processes | Yes | Yes | `multiprocessing` |
| Coroutines | Yes | No | `asyncio` |

## The Fundamental Challenge

Starting threads or processes is easy. The hard part is **coordination**:

- **Knowing when work is done.** Unlike a function call that blocks and returns, a thread or process runs independently. You need an explicit communication channel (queue, event, future) to learn when it finishes.
- **Getting results back.** Objects crossing process boundaries must be serialized. Threads share memory, which is fast but risks data corruption without locks.
- **Amortizing startup costs.** Threads and processes are expensive to create, so they are typically long-lived workers consuming from a queue.
- **Shutting down cleanly.** You cannot forcibly terminate a thread in Python. You must send it a signal (e.g., a `threading.Event`) and let it exit on its own terms.

Coroutines are cheaper to start and easier to cancel, but they are cooperative: a coroutine that blocks without yielding (`await`) freezes the entire event loop.

## Key Vocabulary

- **Execution unit**: anything that runs code concurrently (process, thread, or coroutine).
- **Preemptive multitasking**: the OS can suspend any thread/process at any time.
- **Cooperative multitasking**: the running coroutine must explicitly yield control via `await`.
- **Queue**: the primary data structure for exchanging data and control signals between execution units.
- **Lock / Mutex**: prevents concurrent access to shared data. Threads need them; coroutines generally do not.
- **Contention**: competition for a limited resource (a lock, CPU time, etc.).

## Connection to Other Concepts

Understanding this distinction is foundational for the rest of Chapter 19 and the two chapters that follow (concurrent.futures in Chapter 20, asyncio in Chapter 21). Every design decision -- threads vs processes vs coroutines -- flows from whether your workload is I/O-bound (concurrency suffices) or CPU-bound (parallelism required).
