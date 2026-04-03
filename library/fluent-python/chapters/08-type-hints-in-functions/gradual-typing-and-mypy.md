---
title: "Gradual Typing and Mypy"
book: "Fluent Python"
chapter: 8
tags: [python, type-hints, gradual-typing, mypy, static-analysis]
related:
  - "[[any-optional-union]]"
  - "[[static-protocols]]"
  - "[[typevar-and-parameterized-generics]]"
---

# Gradual Typing and Mypy

Python's gradual type system, introduced by PEP 484, lets you add type hints incrementally to your codebase. Hints are always optional, completely ignored at runtime, and checked only by external tools like Mypy, Pyright, Pyre, or pytype. This means you can mix annotated and unannotated code freely, adopting type checking at whatever pace suits your project.

## How It Works

A gradual type system has three defining properties:

1. **Optional**: The type checker assumes `Any` for unannotated code and emits no warnings. You can annotate one function at a time.
2. **Not enforced at runtime**: Type hints are metadata stored in `__annotations__` but never checked by the Python interpreter during execution.
3. **No performance impact**: The runtime ignores annotations entirely. (JIT compilers like PyPy use their own runtime profiling, which is more accurate than static hints.)

Here is a practical workflow showing gradual annotation guided by Mypy:

```python
# Step 0: No hints -- Mypy ignores this function entirely
def show_count(count, word):
    if count == 1:
        return f"1 {word}"
    count_str = str(count) if count else "no"
    return f"{count_str} {word}s"

# Step 1: Add just the return type -- Mypy now inspects this function
def show_count(count, word) -> str:
    ...

# Mypy reports: Function is missing a type annotation for one or more arguments

# Step 2: Fully annotated -- Mypy is satisfied
def show_count(count: int, word: str) -> str:
    if count == 1:
        return f"1 {word}"
    count_str = str(count) if count else "no"
    return f"{count_str} {word}s"
```

The `--disallow-incomplete-defs` flag is ideal for gradual adoption: it only complains about functions that are partially annotated, leaving fully unannotated functions alone.

### Duck Typing vs Nominal Typing

Python's gradual type system bridges two worldviews:

- **Duck typing** (runtime): Objects have types, but variables do not. If an object supports the needed operations, it works. This is Python's traditional model.
- **Nominal typing** (static): The declared type of a variable determines what operations the type checker allows. `Duck` is a subclass of `Bird`, so a `Duck` can substitute for a `Bird` -- but the type checker only allows methods declared on `Bird`.

```python
class Bird:
    pass

class Duck(Bird):
    def quack(self):
        print("Quack!")

def alert_bird(birdie: Bird) -> None:
    birdie.quack()  # Mypy error: "Bird" has no attribute "quack"

# At runtime, alert_bird(Duck()) works fine -- duck typing wins.
# But Mypy flags it because Bird's interface doesn't include quack().
```

This tension is resolved by [[static-protocols]], which bring duck typing into the static world.

## In Practice

- **Start with `--disallow-incomplete-defs`** rather than `--disallow-untyped-defs`. This lets you annotate gradually without being bombarded by warnings on every unannotated function.
- **Use a `mypy.ini` or `pyproject.toml`** to store your preferred settings so the team shares the same strictness level.
- **Annotate public APIs first**, then internal helpers. The biggest payoff comes from documenting function boundaries.
- **CI integration**: Add Mypy to your CI pipeline alongside tests and linters. It catches a different class of bugs than tests do.

A minimal `mypy.ini`:

```ini
[mypy]
python_version = 3.11
warn_unused_configs = True
disallow_incomplete_defs = True
```

## Common Pitfalls

- **Confusing `color=str` with `color: str`**: Writing `color=str` sets the default value to the `str` class itself. The annotation syntax is `color: str`. This is a common typo that Mypy reports unhelpfully as "Function is missing a type annotation for one or more arguments."
- **Expecting runtime enforcement**: Type hints are not contracts. Passing `"hello"` to a parameter annotated `int` will not raise a `TypeError` at runtime -- it only matters to the type checker.
- **Seeking 100% annotation coverage**: Forcing type hints everywhere can make code harder to read and prevent you from using Python's dynamic strengths. Annotate where it adds value.
- **Ignoring `# type: ignore` discipline**: Use targeted ignore comments (`# type: ignore[attr-defined]`) rather than blanket suppression, so you do not mask real errors.

## See Also

- [[any-optional-union]] -- The `Any` type is central to how gradual typing works
- [[static-protocols]] -- Bridges duck typing and nominal typing via structural subtyping
- [[typevar-and-parameterized-generics]] -- Adds expressiveness to type hints without sacrificing safety
- PEP 484 -- Type Hints: the foundational PEP
- PEP 483 -- The Theory of Type Hints: the theoretical background
- Mypy documentation: https://mypy.readthedocs.io/
