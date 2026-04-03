---
title: "Custom Formatting: __format__ with Spherical Coordinates"
book: "Fluent Python"
chapter: 12
tags: [python, __format__, format-mini-language, hyperspherical-coordinates, itertools-chain, generator-expressions]
type: "code-heavy"
depends_on:
  - "[[vector-multidimensional-sequence]]"
  - "[[hashing-and-eq]]"
related:
  - "[[protocols-and-duck-typing]]"
  - "[[dynamic-attribute-access]]"
  - "[[string-representation]]"
---

## Summary

The `__format__` method on `Vector` extends the Format Specification Mini-Language with a custom `'h'` suffix for **hyperspherical coordinates** (the N-dimensional generalization of polar/spherical coordinates). When the format spec ends with `'h'`, the vector displays as `<r, phi1, phi2, ...>` with angle brackets, where `r` is the magnitude and the remaining values are angular coordinates. Without `'h'`, it shows Cartesian coordinates in parentheses: `(x, y, z, ...)`. The implementation uses `itertools.chain` to seamlessly concatenate the magnitude with the angular components, and generator expressions throughout for memory efficiency.

## How It Works

### The Format Mini-Language Extension

Python's `format()` function calls `obj.__format__(fmt_spec)`. The format spec is whatever appears after the colon in an f-string or `format()` call:

```python
format(v, '.3eh')   # fmt_spec = '.3eh'
f'{v:.3eh}'         # same thing
```

Our extension interprets the last character:

| Suffix | Meaning | Output style | Example |
|--------|---------|-------------|---------|
| (none) | Cartesian | `(x, y, z)` | `(3.0, 4.0, 5.0)` |
| `'h'` | Hyperspherical | `<r, phi1, phi2>` | `<7.071, 0.955, 0.785>` |

Everything before the `'h'` is a standard float format spec (`.2f`, `.3e`, etc.) applied to each individual coordinate.

### Choosing `'h'`

When extending the format mini-language, you must avoid collisions with existing format codes. The built-in float codes are `'eEfFgGn%'`, integers use `'bcdoxXn'`, and strings use `'s'`. The `Vector2d` class in Chapter 11 used `'p'` for polar coordinates. `'h'` for hyperspherical is safe and mnemonic.

### The Implementation

```python
import itertools

def angle(self, n):
    """Compute the n-th angular coordinate (1-indexed)."""
    r = math.hypot(*self[n:])
    a = math.atan2(r, self[n - 1])
    if (n == len(self) - 1) and (self[-1] < 0):
        return math.pi * 2 - a
    return a

def angles(self):
    """Generator yielding all angular coordinates."""
    return (self.angle(n) for n in range(1, len(self)))

def __format__(self, fmt_spec=''):
    if fmt_spec.endswith('h'):
        fmt_spec = fmt_spec[:-1]           # strip the 'h'
        coords = itertools.chain(
            [abs(self)],                    # magnitude r
            self.angles()                   # angular coordinates
        )
        outer_fmt = '<{}>'                  # angle brackets
    else:
        coords = self                       # Cartesian components
        outer_fmt = '({})'                  # parentheses
    components = (format(c, fmt_spec) for c in coords)
    return outer_fmt.format(', '.join(components))
```

### Step by Step

1. **Detect the suffix**: If `fmt_spec` ends with `'h'`, strip it and switch to spherical mode.
2. **Build the coordinate source**:
   - Spherical: `itertools.chain([abs(self)], self.angles())` produces the magnitude followed by all angles, as a single lazy iterator.
   - Cartesian: Just `self` (the vector is iterable).
3. **Format each coordinate**: A generator expression applies the float format spec to each value.
4. **Join and wrap**: `', '.join(components)` produces the comma-separated string, wrapped in either `<>` or `()`.

### `itertools.chain` in Detail

`itertools.chain(iter1, iter2, ...)` produces all items from `iter1`, then all from `iter2`, and so on, without creating an intermediate list:

```python
>>> list(itertools.chain([10], (20, 30)))
[10, 20, 30]
```

Here it concatenates a single-element list `[abs(self)]` with the generator from `self.angles()`. This is cleaner than manually yielding the magnitude and then the angles in a custom generator.

### The Angular Coordinate Math

The `angle(n)` method computes the n-th angular coordinate using the conversion from Cartesian to hyperspherical coordinates. The formula involves `math.atan2` and `math.hypot` over slices of the vector:

```python
def angle(self, n):
    r = math.hypot(*self[n:])
    a = math.atan2(r, self[n - 1])
    if (n == len(self) - 1) and (self[-1] < 0):
        return math.pi * 2 - a
    return a
```

The special case for the last angle (`n == len(self) - 1`) handles the sign convention: when the last component is negative, the angle wraps around to the range `[pi, 2*pi)` instead of `[0, pi)`.

## In Practice

```python
# 2D: radius and angle (like polar coordinates)
>>> format(Vector([1, 1]), 'h')
'<1.4142135623730951, 0.7853981633974483>'

# 3D with scientific notation
>>> format(Vector([2, 2, 2]), '.3eh')
'<3.464e+00, 9.553e-01, 7.854e-01>'

# 4D with fixed-point
>>> format(Vector([0, 1, 0, 0]), '0.5fh')
'<1.00000, 1.57080, 0.00000, 0.00000>'

# Cartesian (default)
>>> format(Vector([3, 4, 5]))
'(3.0, 4.0, 5.0)'

# Cartesian with formatting
>>> format(Vector([3, 4]), '.2f')
'(3.00, 4.00)'
```

The Cartesian output shows all components without truncation. For vectors with many dimensions, this could produce very long strings. The author notes this is intentional: `__format__` output is for end users who presumably want to see everything. If truncation is needed, one could extend the mini-language with a `*` suffix for "show all" vs. a default limit.

## Generator Expressions Everywhere

The `__format__` method, `angle()`, and `angles()` all use generator expressions. This is a deliberate choice:

- **Memory**: No intermediate lists are created. For a 10,000-dimension vector, the spherical representation is computed one coordinate at a time.
- **Laziness**: Angular coordinates are computed on demand. If `format()` were somehow interrupted early, unused angles would never be computed.

These generators are covered in depth in Chapter 17.

## Gotchas

- **No truncation in `__format__`**: Unlike `__repr__` (which uses `reprlib` to limit length), `__format__` shows everything. For very large vectors, the formatted string could be enormous.
- **`itertools.chain` vs `[*a, *b]`**: Unpacking into a list (`[abs(self), *self.angles()]`) would create a full list in memory. `chain` keeps it lazy.
- **Format spec parsing is fragile**: The current implementation simply checks `endswith('h')`. A more robust approach would use regex to separate the float spec from the coordinate-system suffix, but for this educational example, simplicity wins.
- **Coordinate math edge cases**: When the magnitude is zero, all angles are undefined. The current implementation handles this through `math.atan2(0, 0)` returning 0.0, which is a reasonable convention.

## See Also

- [[vector-multidimensional-sequence]] -- The baseline class
- [[hashing-and-eq]] -- The immediately preceding version of Vector
- [[string-representation]] -- Chapter 1/11's treatment of `__repr__` vs `__str__` vs `__format__`
- [[protocols-and-duck-typing]] -- Why `__format__` is part of a broader protocol
