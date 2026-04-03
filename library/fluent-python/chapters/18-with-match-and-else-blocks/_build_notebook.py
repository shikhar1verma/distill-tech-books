"""Build the Chapter 18 interactive notebook."""
import sys
sys.path.insert(0, "/Users/olympus/projects/distill-tech-books/src")
from notebook_builder import build_notebook

TITLE = "Chapter 18: with, match, and else Blocks"
OUTPUT = "/Users/olympus/projects/distill-tech-books/library/fluent-python/chapters/18-with-match-and-else-blocks/chapter-18-with-match-and-else-blocks.ipynb"

cells = [
    # ── Title ──────────────────────────────────────────────
    {"type": "markdown", "content": """# Chapter 18: with, match, and else Blocks
*Fluent Python, 2nd Edition — Luciano Ramalho*

This notebook distills the key ideas from Chapter 18:

1. **Context Managers and the `with` Statement** — the `__enter__`/`__exit__` protocol
2. **The `contextlib` Utilities** — `closing`, `suppress`, `nullcontext`, `ExitStack`
3. **`@contextmanager`** — building context managers from generators
4. **Pattern Matching beyond sequences** — class patterns, guards, OR-patterns
5. **`else` blocks beyond `if`** — `for/else`, `while/else`, `try/else`

Every code cell is self-contained and runnable on Python 3.11+."""},

    # ── 1. Context Managers and the with Statement ─────────
    {"type": "markdown", "content": """---
## 1. Context Managers and the `with` Statement

A context manager is any object that implements `__enter__` and `__exit__`.
The `with` statement calls `__enter__` at the top and `__exit__` when the block
finishes (or raises). Key insight: the *context manager* (the object after `with`)
is **not** necessarily the same as the value bound by `as` (the return of `__enter__`).

### File objects as context managers"""},

    {"type": "code", "content": """# The classic example: files are context managers.
# __enter__ returns self; __exit__ closes the file.
import tempfile, os

path = os.path.join(tempfile.gettempdir(), \"_ch18_demo.txt\")
with open(path, \"w\") as fp:
    fp.write(\"hello from with block\")
    print(f\"Inside with: fp.closed = {fp.closed}\")

print(f\"Outside with: fp.closed = {fp.closed}\")
# fp is still accessible (with blocks don't create a new scope)
print(f\"fp.name = {fp.name}\")
os.remove(path)"""},

    {"type": "markdown", "content": """### Writing a custom context manager class

The `LookingGlass` example from the book: inside the `with` block, all
`sys.stdout.write` calls reverse their text."""},

    {"type": "code", "content": """import sys

class LookingGlass:
    \"\"\"Context manager that reverses stdout writes inside the with block.\"\"\"

    def __enter__(self):
        self.original_write = sys.stdout.write
        sys.stdout.write = self._reverse_write
        return 'JABBERWOCKY'          # bound to the `as` variable

    def _reverse_write(self, text):
        self.original_write(text[::-1])

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout.write = self.original_write   # always restore
        if exc_type is ZeroDivisionError:
            print('Please DO NOT divide by zero!')
            return True   # suppress the exception
        # returning None (falsy) propagates any other exception

# --- demo ---
with LookingGlass() as what:
    print('Alice, Kitty and Snowdrop')   # printed reversed
    print(what)                           # printed reversed

print(f'Back to normal. what = {what!r}')"""},

    {"type": "markdown", "content": """### The `__exit__` signature

```python
def __exit__(self, exc_type, exc_value, traceback):
```

- If the `with` block completes normally, all three are `None`.
- If an exception occurred, they hold the exception class, instance, and traceback.
- Returning a truthy value from `__exit__` **suppresses** the exception."""},

    {"type": "code", "content": """# Demonstrate using a context manager *without* a with block
manager = LookingGlass()
monster = manager.__enter__()
print(f\"monster = {monster!r}\")    # reversed!
manager.__exit__(None, None, None)
print(f\"monster = {monster!r}\")    # normal again"""},

    # ── 2. contextlib Utilities ────────────────────────────
    {"type": "markdown", "content": """---
## 2. The `contextlib` Utilities

The `contextlib` module provides building blocks so you rarely need to write
a full class:

| Utility | Purpose |
|---------|---------|
| `closing(thing)` | Wraps objects with `.close()` but no `__enter__/__exit__` |
| `suppress(*exceptions)` | Silently ignore specified exceptions |
| `nullcontext(enter_result=None)` | No-op CM; useful for conditional CM logic |
| `redirect_stdout(new_target)` | Redirect `sys.stdout` into a file-like object |
| `redirect_stderr(new_target)` | Same for `sys.stderr` |
| `ExitStack` | Manage a dynamic number of context managers |
| `@contextmanager` | Build a CM from a generator (next section) |
| `AbstractContextManager` | ABC to subclass for custom CM classes |
| `ContextDecorator` | CM that doubles as a function decorator |"""},

    {"type": "code", "content": """from contextlib import suppress, redirect_stdout, nullcontext
import io

# --- suppress: ignore specific exceptions ---
d = {'a': 1}
with suppress(KeyError):
    val = d['missing_key']   # KeyError raised and silenced
print(\"After suppress: no crash\")

# --- redirect_stdout: capture print output ---
buf = io.StringIO()
with redirect_stdout(buf):
    print(\"This goes into buf, not the console\")
print(f\"Captured: {buf.getvalue()!r}\")

# --- nullcontext: conditional context manager ---
verbose = False
cm = redirect_stdout(io.StringIO()) if verbose else nullcontext()
with cm:
    print(\"This prints normally because verbose=False\")"""},

    {"type": "code", "content": """from contextlib import ExitStack
import tempfile, os

# ExitStack manages a dynamic number of context managers
paths = []
for i in range(3):
    paths.append(os.path.join(tempfile.gettempdir(), f\"_ch18_es_{i}.txt\"))

with ExitStack() as stack:
    files = [stack.enter_context(open(p, 'w')) for p in paths]
    for i, f in enumerate(files):
        f.write(f\"file {i}\")
    print(f\"Inside: all {len(files)} files open\")

print(f\"Outside: all closed? {all(f.closed for f in files)}\")
for p in paths:
    os.remove(p)"""},

    # ── 3. @contextmanager ─────────────────────────────────
    {"type": "markdown", "content": """---
## 3. Using `@contextmanager`

The `@contextlib.contextmanager` decorator turns a generator with a
**single `yield`** into a full context manager:

- Everything **before** `yield` runs on `__enter__`
- The yielded value is bound to the `as` variable
- Everything **after** `yield` runs on `__exit__`

You **must** wrap `yield` in `try/finally` if cleanup is critical."""},

    {"type": "code", "content": """import contextlib
import sys

@contextlib.contextmanager
def looking_glass():
    \"\"\"Generator-based version of the LookingGlass context manager.\"\"\"
    original_write = sys.stdout.write

    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write
    msg = ''
    try:
        yield 'JABBERWOCKY'
    except ZeroDivisionError:
        msg = 'Please DO NOT divide by zero!'
    finally:
        sys.stdout.write = original_write  # always restore
        if msg:
            print(msg)

# --- demo ---
with looking_glass() as what:
    print('Alice, Kitty and Snowdrop')
    print(what)

print(f'Back to normal. what = {what!r}')"""},

    {"type": "markdown", "content": """### `@contextmanager` as a decorator

Because `@contextmanager` is built on `ContextDecorator`, the resulting
context manager can also be used as a **function decorator**:"""},

    {"type": "code", "content": """@looking_glass()
def verse():
    print('The time has come')

verse()       # output is reversed
print('back to normal')"""},

    {"type": "markdown", "content": """### How `@contextmanager` works internally

1. Calls the generator function to get a generator `gen`
2. `__enter__` calls `next(gen)` to advance to `yield` and returns the yielded value
3. `__exit__` calls `next(gen)` if no exception, or `gen.throw(exception)` if one occurred

The **default behavior is inverted** compared to a class-based CM: with
`@contextmanager`, if you catch an exception around `yield` and don't re-raise it,
the exception is suppressed."""},

    # ── 4. Pattern Matching Beyond Sequences ───────────────
    {"type": "markdown", "content": """---
## 4. Pattern Matching Beyond Sequences

Chapter 18 uses Norvig's `lis.py` Scheme interpreter to demonstrate
`match/case` with:

- **Class patterns**: `int(x)`, `float(x)`, `str(var)` -- match by type and capture
- **Sequence patterns with guards**: `['lambda', [*parms], *body] if body`
- **OR-patterns**: `int(x) | float(x)` -- match if *any* alternative matches
- **Wildcard**: `case _:` catches everything else

Below we build a **mini expression evaluator** inspired by `lis.py`."""},

    {"type": "code", "content": """# A tiny expression evaluator using match/case
# Supports: numbers, +, -, *, /, nested expressions
from typing import Any

def evaluate(exp: Any) -> float:
    \"\"\"Evaluate a nested-list expression.

    Examples:
        evaluate(42)              -> 42
        evaluate(['+', 1, 2])     -> 3
        evaluate(['*', ['+', 1, 2], ['-', 10, 3]])  -> 21
    \"\"\"
    match exp:
        case int(x) | float(x):           # number literal
            return x
        case ['+', a, b]:                  # addition
            return evaluate(a) + evaluate(b)
        case ['-', a, b]:                  # subtraction
            return evaluate(a) - evaluate(b)
        case ['*', a, b]:                  # multiplication
            return evaluate(a) * evaluate(b)
        case ['/', a, b]:                  # division
            return evaluate(a) / evaluate(b)
        case [op, *args] if callable(op):  # direct callable
            return op(*(evaluate(a) for a in args))
        case _:
            raise SyntaxError(f\"Unknown expression: {exp!r}\")

# --- tests ---
print(evaluate(42))
print(evaluate(['+', 1, 2]))
print(evaluate(['*', ['+', 1, 2], ['-', 10, 3]]))
print(evaluate(['/', 355, 113]))   # approx pi"""},

    {"type": "markdown", "content": """### Class patterns and guard clauses

Class patterns like `Symbol(var)` match instances of a type and bind the first
positional attribute. For built-in types like `int`, `float`, `str`, this
captures the value itself.

Guard clauses (`if body`) add extra conditions after the structural match:

```python
case ['lambda', [*parms], *body] if body:
    # only matches if body is non-empty
```"""},

    {"type": "code", "content": """# Demonstrate class patterns with a custom class
class Command:
    \"\"\"Simple class to demonstrate class patterns.\"\"\"
    __match_args__ = ('action', 'target')  # positional match support

    def __init__(self, action: str, target: str):
        self.action = action
        self.target = target

def handle(cmd):
    match cmd:
        case Command(action='quit', target=_):
            return 'Quitting...'
        case Command(action='greet', target=name):
            return f'Hello, {name}!'
        case Command(action=a, target=t) if a.startswith('delete'):
            return f'DANGER: {a} on {t}'
        case _:
            return f'Unknown command: {cmd}'

print(handle(Command('greet', 'Alice')))
print(handle(Command('quit', '')))
print(handle(Command('delete_all', 'database')))
print(handle(Command('fly', 'moon')))"""},

    # ── 5. OR-patterns ─────────────────────────────────────
    {"type": "markdown", "content": """---
## 5. OR-patterns in `match/case`

Subpatterns joined by `|` form an OR-pattern. Rules:
- Succeeds if **any** alternative matches
- All alternatives **must bind the same set of variables**
- Can appear at the top level or nested inside a larger pattern"""},

    {"type": "code", "content": """# OR-patterns: top-level and nested

def classify(value):
    match value:
        case int(x) | float(x):
            return f'number: {x}'
        case str(s):
            return f'string: {s!r}'
        case [('yes' | 'on' | 'true'), *rest]:    # nested OR-pattern
            return f'truthy flag with extras: {rest}'
        case [('no' | 'off' | 'false'), *rest]:
            return f'falsy flag with extras: {rest}'
        case _:
            return f'other: {value!r}'

print(classify(3.14))
print(classify(42))
print(classify('hello'))
print(classify(['yes', 'verbose']))
print(classify(['off']))
print(classify(['no', 'debug', 'trace']))"""},

    # ── 6. else Blocks Beyond if ───────────────────────────
    {"type": "markdown", "content": """---
## 6. `else` Blocks Beyond `if`

Python allows `else` on three additional compound statements:

| Statement | `else` runs when... |
|-----------|---------------------|
| `for ... else` | Loop completes **without** `break` |
| `while ... else` | Condition becomes falsy (no `break`) |
| `try ... else` | No exception was raised in `try` block |

Think of `else` as meaning **"then"** (do this, *then* that) rather than
"otherwise"."""},

    {"type": "code", "content": """# --- for/else: search with break ---
fruits = ['apple', 'mango', 'banana', 'cherry']

def find_fruit(target, basket):
    for fruit in basket:
        if fruit == target:
            print(f'Found {target}!')
            break
    else:
        # Runs only if we did NOT break (item not found)
        print(f'{target} not in basket')

find_fruit('banana', fruits)
find_fruit('grape', fruits)"""},

    {"type": "code", "content": """# --- while/else ---
n = 5
while n > 0:
    n -= 1
else:
    print(f'while finished normally (n={n})')

# contrast: break prevents else
n = 5
while n > 0:
    n -= 1
    if n == 2:
        print(f'Breaking at n={n}')
        break
else:
    print('This will NOT print because we broke out')"""},

    {"type": "code", "content": """# --- try/else: separate guarded code from follow-up ---
import json

def safe_parse(text):
    \"\"\"Parse JSON; the else block runs only if parsing succeeds.\"\"\"
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f'Parse error: {e}')
    else:
        # This runs ONLY if no exception was raised in try
        # Exceptions here are NOT caught by the except above
        print(f'Parsed successfully: {data}')
        return data

safe_parse('{\"key\": \"value\"}')
safe_parse('not valid json {{{')"""},

    {"type": "markdown", "content": """### EAFP vs LBYL

The `try/else` pattern supports **EAFP** (Easier to Ask Forgiveness than Permission):
put the risky call in `try`, handle failures in `except`, and put the success
path in `else`. This is cleaner than **LBYL** (Look Before You Leap), which uses
`if` checks that can introduce race conditions in concurrent code."""},

    {"type": "code", "content": """# EAFP style with try/else
config = {'timeout': '30', 'retries': '3', 'debug': 'not_a_number'}

def get_int_setting(settings, key, default=0):
    \"\"\"EAFP: try to convert, handle failure gracefully.\"\"\"
    try:
        raw = settings[key]
    except KeyError:
        return default
    else:
        # Only runs if key was found
        try:
            return int(raw)
        except ValueError:
            print(f'Warning: {key}={raw!r} is not an int, using default')
            return default

print(get_int_setting(config, 'timeout'))
print(get_int_setting(config, 'retries'))
print(get_int_setting(config, 'debug', default=-1))
print(get_int_setting(config, 'missing', default=99))"""},

    # ── Recap ──────────────────────────────────────────────
    {"type": "markdown", "content": """---
## Recap

| Concept | Key Takeaway |
|---------|-------------|
| `with` / Context Managers | `__enter__` sets up, `__exit__` tears down -- even on exceptions |
| `contextlib` | `suppress`, `ExitStack`, `redirect_stdout`, `nullcontext` save boilerplate |
| `@contextmanager` | Generator + single `yield` = lightweight CM; wrap `yield` in `try/finally` |
| `match/case` patterns | Class patterns, guards, sequence patterns, and OR-patterns enable declarative dispatch |
| OR-patterns | `a \\| b` in a `case` clause; all alternatives must bind the same variables |
| `else` beyond `if` | `for/else`, `while/else`, `try/else` -- "then" semantics, not "otherwise" |

**Further exploration:** Try building your own context manager with `@contextmanager`
that times a block of code, or write a mini-DSL evaluator using `match/case`."""},
]

path = build_notebook(TITLE, cells, OUTPUT)
print(f"Notebook created: {path}")
