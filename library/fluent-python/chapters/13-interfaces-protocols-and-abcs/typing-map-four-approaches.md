---
title: "The Typing Map: Four Approaches to Typing"
chapter: 13
slug: typing-map-four-approaches
type: theory-heavy
depends_on: []
tags:
  - typing
  - duck-typing
  - goose-typing
  - static-typing
  - protocols
---

# The Typing Map: Four Approaches to Typing

Python provides four complementary approaches to type checking, each occupying a quadrant in the **Typing Map**.

## The Four Quadrants

### Duck Typing (Runtime + Structural)

Python's default since the beginning. An object's type is determined by the methods it provides, not its class name. The interpreter cooperates deeply with objects that implement key [[dynamic-protocols-and-duck-typing|dynamic protocols]] like `__getitem__`, `__len__`, and `__iter__`.

- **Checked:** at runtime, by the interpreter
- **Defined:** by convention and documentation
- **Strength:** maximum flexibility

### Goose Typing (Runtime + Nominal)

Uses [[goose-typing-and-abcs|abstract base classes (ABCs)]] with `isinstance` and `issubclass` for explicit runtime type checking. Introduced in Python 2.6.

- **Checked:** at runtime, via `isinstance(obj, SomeABC)`
- **Defined:** by `abc.ABC` subclasses
- **Strength:** enforced contracts with flexibility via [[virtual-subclasses-and-register|virtual subclasses]]

### Static Typing (Static + Nominal)

Traditional approach from C and Java. Type annotations checked by external tools (mypy, pyright). Supported since Python 3.5 via PEP 484.

- **Checked:** by external static type checkers
- **Defined:** by type annotations using concrete types or ABCs
- **Strength:** catches bugs before runtime

### Static Duck Typing (Static + Structural)

Enabled by [[static-protocols-typing-protocol|typing.Protocol]] (PEP 544, Python 3.8). Defines interfaces structurally -- any class implementing the required methods is *consistent-with* the protocol. Inspired by Go's interface system.

- **Checked:** by static type checkers + optionally at runtime
- **Defined:** by `typing.Protocol` subclasses
- **Strength:** combines static checking with duck typing flexibility

## Key Insight

All four approaches revolve around **interfaces** -- the methods an object provides. The difference is in *when* and *how* the interface conformance is checked. Rejecting any one approach makes your work as a Python programmer harder than it needs to be.

## See Also

- [[dynamic-protocols-and-duck-typing]] -- duck typing in depth
- [[goose-typing-and-abcs]] -- ABCs and isinstance
- [[static-protocols-typing-protocol]] -- typing.Protocol
- [[typing-map-four-approaches]] -- choosing the right approach
