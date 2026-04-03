---
title: "Error Handling and Progress Display"
slug: error-handling-concurrent
chapter: 20
book: fluent-python
type: code-heavy
depends_on:
  - future-objects
tags: [concurrency, error-handling, as-completed, progress, tqdm, futures]
---

# Error Handling and Progress Display

## Core Idea

Real concurrent code must handle errors gracefully. The book's `flags2` examples demonstrate the production-ready pattern: use `executor.submit()` with `futures.as_completed()`, mapping each Future to its context in a dict, then handle exceptions per-task as results arrive.

This pattern also enables progress display (e.g., with `tqdm`) because you process results as they complete rather than waiting in submission order.

## The `future -> context` Dict Pattern

This is the most important concurrent.futures idiom for real-world code:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

def download_many(cc_list, base_url, verbose, concur_req):
    counter: Counter[DownloadStatus] = Counter()

    with ThreadPoolExecutor(max_workers=concur_req) as executor:
        # Step 1: Submit tasks, mapping each future to its context
        to_do_map: dict[Future, str] = {}
        for cc in sorted(cc_list):
            future = executor.submit(download_one, cc, base_url, verbose)
            to_do_map[future] = cc  # future -> country code

        # Step 2: Wrap with tqdm for progress display
        done_iter = as_completed(to_do_map)
        if not verbose:
            done_iter = tqdm.tqdm(done_iter, total=len(cc_list))

        # Step 3: Process results with per-task error handling
        for future in done_iter:
            try:
                status = future.result()
            except httpx.HTTPStatusError as exc:
                error_msg = f"HTTP {exc.response.status_code}"
            except httpx.RequestError as exc:
                error_msg = f"{exc}"
            except KeyboardInterrupt:
                break
            else:
                error_msg = ''

            if error_msg:
                status = DownloadStatus.ERROR
            counter[status] += 1

            # Context from the dict enables useful error messages
            if verbose and error_msg:
                cc = to_do_map[future]  # <-- look up context!
                print(f'{cc} error: {error_msg}')

    return counter
```

## Why This Pattern Works

1. **`to_do_map[future] = cc`** -- at submission time, you know the context (country code, URL, task ID, etc.). Store it keyed by the future.

2. **`as_completed` yields in completion order** -- so `tqdm` can update the progress bar as each task finishes, giving real-time feedback.

3. **`future.result()` inside `try/except`** -- since `as_completed` only yields done futures, `result()` never blocks; it either returns the value or raises the exception from the callable.

4. **`to_do_map[future]`** -- when an error occurs, you look up the context to produce a useful error message. Without this dict, you would not know which task failed (since `as_completed` returns futures in arbitrary order).

## Error Strategy in the Book

The `flags2` examples use a two-level error strategy:

| Error type | Handled by | Action |
|---|---|---|
| HTTP 404 (Not Found) | `download_one` | Return `DownloadStatus.NOT_FOUND` |
| Other HTTP errors | `download_many` | Log error, count as `ERROR` |
| Network errors | `download_many` | Log error, count as `ERROR` |
| `KeyboardInterrupt` | `download_many` | Break out of loop |
| Unexpected exceptions | Propagate up | Crash with traceback |

The key design: the per-file function (`download_one`) handles expected per-file errors (404). The orchestrator (`download_many`) handles broader errors and tallies results.

## Integrating tqdm Progress Bars

Since `as_completed` returns an iterator, wrapping it with `tqdm` is trivial:

```python
done_iter = as_completed(to_do_map)
if not verbose:
    done_iter = tqdm.tqdm(done_iter, total=len(cc_list))
```

You must pass `total=` because the iterator from `as_completed` has no `len`. Each completed future advances the progress bar by one.

## See Also

- [[future-objects]] -- Fundamentals of Future objects and `as_completed`
- [[thread-pool-executor]] -- Simpler cases with `executor.map`
- [[executor-map-behavior]] -- Why `map` is insufficient for error handling
