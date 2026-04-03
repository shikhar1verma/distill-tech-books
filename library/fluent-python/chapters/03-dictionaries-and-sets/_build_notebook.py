#!/usr/bin/env python3
"""Build the Chapter 3 interactive notebook."""
import sys
sys.path.insert(0, "/Users/olympus/projects/distill-tech-books/src")
from notebook_builder import build_notebook

cells = [
    # ── Title ──────────────────────────────────────────────────────────
    {"type": "markdown", "content": """# Chapter 3: Dictionaries and Sets
*Fluent Python, 2nd Edition -- Luciano Ramalho*

> "Python is basically dicts wrapped in loads of syntactic sugar." -- Lalo Martins

---

## TL;DR

- **Dict comprehensions** (`{k: v for k, v in items}`) build dicts concisely; `**` unpacks mappings; `|` / `|=` (3.9+) merge them.
- **Pattern matching** with `match/case` (3.10+) destructures mappings, succeeding on **partial** matches.
- Dict keys and set elements must be **hashable** (constant `__hash__` + `__eq__`).
- **`defaultdict`** auto-creates missing values; the **`__missing__`** dunder lets you customize key-not-found behavior.
- The `collections` module provides **`OrderedDict`**, **`ChainMap`**, **`Counter`**, and **`UserDict`** (the safe base class for custom mappings).
- **`MappingProxyType`** gives you a read-only view of a dict; dictionary views (`.keys()`, `.items()`) support set operations.
- **`set`** and **`frozenset`** support fast membership testing and full math-set operations (`|`, `&`, `-`, `^`).

See also: [[hashability]], [[defaultdict-and-missing]], [[dict-variations]], [[set-theory-and-operations]]"""},

    # ── 1. Dict Comprehensions ─────────────────────────────────────────
    {"type": "markdown", "content": """---
## 1. Dict Comprehensions, Unpacking, and Merging

A **dict comprehension** builds a `dict` from any iterable of key-value pairs, just like a list comprehension builds a list.

See also: [[dict-comprehensions-unpacking-merging]]"""},

    {"type": "code", "content": """# Dict comprehension: swap key/value from a list of tuples
dial_codes = [
    (880, 'Bangladesh'), (55, 'Brazil'), (86, 'China'),
    (91, 'India'), (62, 'Indonesia'), (81, 'Japan'),
    (234, 'Nigeria'), (92, 'Pakistan'), (7, 'Russia'),
    (1, 'United States'),
]

country_dial = {country: code for code, country in dial_codes}
print(country_dial)"""},

    {"type": "code", "content": """# Filtering + transforming inside a dictcomp
small_codes = {
    code: country.upper()
    for country, code in sorted(country_dial.items())
    if code < 70
}
print(small_codes)"""},

    {"type": "markdown", "content": """### Unpacking Mappings with `**`

`**` can unpack multiple mappings in a function call or inside a dict literal. Later keys overwrite earlier ones."""},

    {"type": "code", "content": """# ** in function calls
def dump(**kwargs):
    return kwargs

result = dump(**{'x': 1}, y=2, **{'z': 3})
print(result)  # {'x': 1, 'y': 2, 'z': 3}"""},

    {"type": "code", "content": """# ** inside dict literals -- duplicates: last wins
merged = {'a': 0, **{'x': 1}, 'y': 2, **{'z': 3, 'x': 4}}
print(merged)  # 'x' is 4, not 1"""},

    {"type": "markdown", "content": """### Merging with `|` and `|=` (Python 3.9+)

`|` creates a **new** dict; `|=` updates in place. Right-hand values win on key collisions."""},

    {"type": "code", "content": """d1 = {'a': 1, 'b': 3}
d2 = {'a': 2, 'b': 4, 'c': 6}

# | creates a new dict (d1 unchanged)
print(d1 | d2)   # {'a': 2, 'b': 4, 'c': 6}
print(d1)         # still {'a': 1, 'b': 3}

# |= updates d1 in place
d1 |= d2
print(d1)         # {'a': 2, 'b': 4, 'c': 6}"""},

    # ── 2. Pattern Matching ────────────────────────────────────────────
    {"type": "markdown", "content": """---
## 2. Pattern Matching with Mappings (Python 3.10+)

`match/case` destructures mapping objects. Patterns look like dict literals and succeed on **partial** matches -- extra keys in the subject are simply ignored.

See also: [[pattern-matching-mappings]]"""},

    {"type": "code", "content": """def get_creators(record: dict) -> list:
    \"\"\"Extract creator names from media records.\"\"\"
    match record:
        case {'type': 'book', 'api': 2, 'authors': [*names]}:
            return names
        case {'type': 'book', 'api': 1, 'author': name}:
            return [name]
        case {'type': 'book'}:
            raise ValueError(f"Invalid 'book' record: {record!r}")
        case {'type': 'movie', 'director': name}:
            return [name]
        case _:
            raise ValueError(f'Invalid record: {record!r}')

# Test it
b1 = dict(api=1, author='Douglas Hofstadter',
          type='book', title='Godel, Escher, Bach')
print(get_creators(b1))  # ['Douglas Hofstadter']

from collections import OrderedDict
b2 = OrderedDict(api=2, type='book',
                 title='Python in a Nutshell',
                 authors='Martelli Ravenscroft Holden'.split())
print(get_creators(b2))  # ['Martelli', 'Ravenscroft', 'Holden']

movie = {'type': 'movie', 'director': 'Wes Anderson', 'year': 2023}
print(get_creators(movie))  # ['Wes Anderson'] -- partial match OK"""},

    {"type": "code", "content": """# Capture extra keys with **details
food = dict(category='ice cream', flavor='vanilla', cost=199)
match food:
    case {'category': 'ice cream', **details}:
        print(f'Ice cream details: {details}')
    case _:
        print('Not ice cream')"""},

    # ── 3. Hashability ─────────────────────────────────────────────────
    {"type": "markdown", "content": """---
## 3. What Is Hashable

A dict key (or set element) must be **hashable**: it needs a `__hash__()` that never changes during its lifetime AND an `__eq__()`. Objects that compare equal must have the same hash.

See also: [[hashability]]

**Rules of thumb:**
- All immutable built-ins (`int`, `float`, `str`, `bytes`, `frozenset`) are hashable.
- A `tuple` is hashable **only if every item inside it is hashable**.
- User-defined objects are hashable by default (`hash` = `id`), unless you override `__eq__` without also defining `__hash__`."""},

    {"type": "code", "content": """# Tuples: hashable depends on contents
tt = (1, 2, (30, 40))
print(f"hash of nested-tuple: {hash(tt)}")

tf = (1, 2, frozenset([30, 40]))
print(f"hash with frozenset:  {hash(tf)}")

# This will fail:
try:
    tl = (1, 2, [30, 40])
    hash(tl)
except TypeError as e:
    print(f"Cannot hash tuple with list inside: {e}")"""},

    {"type": "code", "content": """# Custom hashable object
class Coord:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __eq__(self, other):
        return isinstance(other, Coord) and (self._x, self._y) == (other._x, other._y)

    def __hash__(self):
        return hash((self._x, self._y))

    def __repr__(self):
        return f'Coord({self._x}, {self._y})'

# Usable as dict keys / set elements
locations = {Coord(0, 0): 'origin', Coord(1, 2): 'point A'}
print(locations[Coord(0, 0)])  # 'origin'
print(Coord(1, 2) in {Coord(1, 2), Coord(3, 4)})  # True"""},

    # ── 4. defaultdict & __missing__ ───────────────────────────────────
    {"type": "markdown", "content": """---
## 4. defaultdict and `__missing__`

### `setdefault` -- the one-lookup pattern

`d.setdefault(key, default)` returns `d[key]` if present, otherwise sets `d[key] = default` and returns it -- in a **single** lookup.

### `defaultdict`

Provide a **callable** (e.g. `list`, `int`, `set`) at construction time. When `d[key]` misses, the callable is invoked to create a default value.

### `__missing__`

If you subclass `dict` and define `__missing__`, it is called by `__getitem__` on key-not-found instead of raising `KeyError`.

See also: [[defaultdict-and-missing]]"""},

    {"type": "code", "content": """# setdefault: build word index in one lookup per word
import re

text = \"\"\"Beautiful is better than ugly
Explicit is better than implicit
Simple is better than complex\"\"\"

index = {}
for line_no, line in enumerate(text.splitlines(), 1):
    for match in re.finditer(r'\\w+', line):
        word = match.group()
        col = match.start() + 1
        index.setdefault(word, []).append((line_no, col))

# Show first few entries
for word in sorted(index)[:5]:
    print(word, index[word])"""},

    {"type": "code", "content": """# defaultdict: same task, even cleaner
from collections import defaultdict

index2 = defaultdict(list)
for line_no, line in enumerate(text.splitlines(), 1):
    for match in re.finditer(r'\\w+', line):
        word = match.group()
        col = match.start() + 1
        index2[word].append((line_no, col))

# Verify identical results
assert dict(index2) == index
print("defaultdict matches setdefault result: OK")

# NOTE: .get() does NOT trigger default_factory
print(index2.get('nonexistent', 'MISSING'))  # 'MISSING', not []"""},

    {"type": "code", "content": """# __missing__: auto-convert int keys to str on lookup
class StrKeyDict(dict):
    \"\"\"Dict that converts non-string keys to str on lookup.\"\"\"

    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)  # prevent infinite recursion
        return self[str(key)]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        return key in self.keys() or str(key) in self.keys()

d = StrKeyDict([('2', 'two'), ('4', 'four')])
print(d['2'])    # 'two'
print(d[4])      # 'four' -- int 4 converted to '4'
print(d.get(1, 'N/A'))  # 'N/A'
print(2 in d)    # True
print(1 in d)    # False"""},

    # ── 5. Dict Variations ─────────────────────────────────────────────
    {"type": "markdown", "content": """---
## 5. Dict Variations: OrderedDict, ChainMap, Counter, UserDict

See also: [[dict-variations]]"""},

    {"type": "code", "content": """from collections import OrderedDict, ChainMap, Counter
import collections

# --- OrderedDict: equality considers key order ---
od1 = OrderedDict(a=1, b=2)
od2 = OrderedDict(b=2, a=1)
print(f"OrderedDict order matters:  {od1 == od2}")  # False

d1 = dict(a=1, b=2)
d2 = dict(b=2, a=1)
print(f"Plain dict ignores order:   {d1 == d2}")     # True

# move_to_end
od1.move_to_end('a')  # move 'a' to the end
print(f"After move_to_end('a'): {list(od1.keys())}")"""},

    {"type": "code", "content": """# --- ChainMap: layered lookup (first map wins) ---
defaults = {'color': 'blue', 'size': 'M'}
user_prefs = {'color': 'red'}
env = {'size': 'XL', 'debug': True}

config = ChainMap(env, user_prefs, defaults)
print(f"color = {config['color']}")   # 'red' (from user_prefs)
print(f"size  = {config['size']}")    # 'XL'  (from env)
print(f"debug = {config['debug']}")   # True   (from env)

# Writes go to the FIRST mapping only
config['theme'] = 'dark'
print(f"env after write: {env}")      # env has 'theme' now"""},

    {"type": "code", "content": """# --- Counter: multiset / tally ---
ct = Counter('abracadabra')
print(ct)                     # Counter({'a': 5, 'b': 2, ...})
print(ct.most_common(3))      # [('a', 5), ('b', 2), ('r', 2)]

ct.update('aaaaazzz')
print(ct.most_common(3))      # [('a', 10), ('z', 3), ('b', 2)]

# Counter arithmetic
ct2 = Counter('abcabc')
print(ct + ct2)               # combined tallies
print(ct - ct2)               # subtract (drops zero/negative)"""},

    {"type": "code", "content": """# --- UserDict: the right base class for custom mappings ---
class StrKeyDict2(collections.UserDict):
    \"\"\"All keys stored as str. Safer than subclassing dict.\"\"\"

    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)
        return self[str(key)]

    def __contains__(self, key):
        return str(key) in self.data   # self.data is the inner dict

    def __setitem__(self, key, item):
        self.data[str(key)] = item     # coerce key on write

d = StrKeyDict2([(2, 'two'), (4, 'four')])
print(d['2'])     # 'two' -- key was stored as '2'
print(d[4])       # 'four'
print(2 in d)     # True
d[10] = 'ten'
print(d['10'])    # 'ten'"""},

    # ── 6. Immutable Mappings & Views ──────────────────────────────────
    {"type": "markdown", "content": """---
## 6. Immutable Mappings and Dictionary Views

### `MappingProxyType` -- read-only wrapper

`types.MappingProxyType(d)` returns a **dynamic, read-only** proxy. You can still modify through the original dict, and changes are visible through the proxy.

### Dictionary views

`.keys()`, `.values()`, `.items()` return lightweight **view** objects (not copies). `dict_keys` and `dict_items` support **set operations**.

See also: [[immutable-mappings-and-views]]"""},

    {"type": "code", "content": """from types import MappingProxyType

d = {1: 'A'}
d_proxy = MappingProxyType(d)

print(d_proxy[1])   # 'A' -- read OK

try:
    d_proxy[2] = 'X'
except TypeError as e:
    print(f"Write blocked: {e}")

# But changes via the original dict are reflected
d[2] = 'B'
print(d_proxy[2])   # 'B' -- dynamic!"""},

    {"type": "code", "content": """# Dictionary views support set operations
d1 = dict(a=1, b=2, c=3, d=4)
d2 = dict(b=20, d=40, e=50)

# Keys in common
print(d1.keys() & d2.keys())   # {'b', 'd'}

# Keys in d1 but not d2
print(d1.keys() - d2.keys())   # {'a', 'c'}

# Mix with a regular set
vowels = {'a', 'e', 'i'}
print(d1.keys() & vowels)      # {'a'}
print(d1.keys() | vowels)      # {'a', 'b', 'c', 'd', 'e', 'i'}"""},

    # ── 7. Set Theory ──────────────────────────────────────────────────
    {"type": "markdown", "content": """---
## 7. Set Theory and Operations

- `set` is mutable; `frozenset` is immutable (and hashable, so it can be a dict key).
- Elements must be hashable.
- `{1, 2, 3}` is a set literal; `set()` for empty (NOT `{}` which is an empty dict!).
- Set comprehensions: `{x**2 for x in range(10)}`.

See also: [[set-theory-and-operations]]"""},

    {"type": "code", "content": """# Removing duplicates, preserving order
items = ['spam', 'spam', 'eggs', 'spam', 'bacon', 'eggs']
unique_ordered = list(dict.fromkeys(items))
print(unique_ordered)  # ['spam', 'eggs', 'bacon']"""},

    {"type": "code", "content": """# Set operations
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

print(f"union        a | b  = {a | b}")
print(f"intersection a & b  = {a & b}")
print(f"difference   a - b  = {a - b}")
print(f"sym_diff     a ^ b  = {a ^ b}")
print(f"subset       a <= b = {a <= b}")
print(f"superset     a >= b = {a >= b}")
print(f"disjoint           = {a.isdisjoint({10, 11})}")"""},

    {"type": "code", "content": """# Practical: fast intersection for membership tests
haystack = set(range(10_000_000))
needles = {3, 7, 42, 9_999_999, -1, 10_000_001}

found = needles & haystack
print(f"Found {len(found)} of {len(needles)} needles: {found}")"""},

    {"type": "code", "content": """# Set comprehension
from unicodedata import name as uname

signs = {chr(i) for i in range(32, 256) if 'SIGN' in uname(chr(i), '')}
print(f"{len(signs)} chars with SIGN in name: {sorted(signs)[:8]} ...")"""},

    {"type": "code", "content": """# frozenset: hashable, usable as dict keys / set elements
fs = frozenset([1, 2, 3])
nested = {fs: 'a frozen set as key'}
print(nested[frozenset([1, 2, 3])])  # 'a frozen set as key'

# set of frozensets
groups = {frozenset([1, 2]), frozenset([3, 4])}
print(groups)"""},

    # ── Exercises ──────────────────────────────────────────────────────
    {"type": "markdown", "content": """---
## Exercises

Test your understanding of this chapter's core ideas."""},

    {"type": "markdown", "content": """### Exercise 1: Dict Comprehension Challenge

Given a dict of product prices, create a new dict containing only products under $50, with prices increased by 10%. Use a dict comprehension."""},

    {"type": "code", "content": """prices = {
    'laptop': 999.99, 'mouse': 29.99, 'keyboard': 49.99,
    'monitor': 299.99, 'usb_cable': 9.99, 'webcam': 39.99,
}

# YOUR CODE HERE: dict comprehension, filter < 50, increase 10%
budget_markup = {
    name: round(price * 1.1, 2)
    for name, price in prices.items()
    if price < 50
}
print(budget_markup)
# Expected: {'mouse': 32.99, 'keyboard': 54.99, 'usb_cable': 10.99, 'webcam': 43.99}"""},

    {"type": "markdown", "content": """### Exercise 2: Implement a defaultdict-like class

Create a class `AutoKeyDict` that subclasses `dict`. When a missing key is accessed, it should automatically create an entry where the value equals the key itself."""},

    {"type": "code", "content": """class AutoKeyDict(dict):
    \"\"\"Missing keys auto-create with value = key.\"\"\"
    def __missing__(self, key):
        self[key] = key
        return key

d = AutoKeyDict(greeting='hello')
print(d['greeting'])  # 'hello'
print(d['world'])     # 'world' -- auto-created
print(d)              # {'greeting': 'hello', 'world': 'world'}"""},

    {"type": "markdown", "content": """### Exercise 3: Set Operations for Data Analysis

Given two sets of student IDs, find: (a) students in both classes, (b) students in class A only, (c) students in exactly one class."""},

    {"type": "code", "content": """class_a = {101, 102, 103, 104, 105, 106}
class_b = {104, 105, 106, 107, 108, 109}

both = class_a & class_b
a_only = class_a - class_b
exactly_one = class_a ^ class_b

print(f"Both classes:      {both}")
print(f"Class A only:      {a_only}")
print(f"Exactly one class: {exactly_one}")"""},

    {"type": "markdown", "content": """### Exercise 4: ChainMap for Config Layers

Create a 3-layer configuration with defaults, environment overrides, and CLI overrides. Verify that the most specific (CLI) layer wins."""},

    {"type": "code", "content": """from collections import ChainMap

defaults = {'debug': False, 'verbose': False, 'port': 8080}
env_cfg  = {'debug': True, 'db_host': 'localhost'}
cli_cfg  = {'port': 9090}

config = ChainMap(cli_cfg, env_cfg, defaults)
print(f"port    = {config['port']}")     # 9090 (CLI wins)
print(f"debug   = {config['debug']}")    # True  (env wins over default)
print(f"verbose = {config['verbose']}")  # False (only in defaults)
print(f"db_host = {config['db_host']}")  # 'localhost' (only in env)"""},

    # ── Takeaways ──────────────────────────────────────────────────────
    {"type": "markdown", "content": """---
## Key Takeaways

1. **Dict comprehensions** are as natural as list comprehensions. Use `|` for merging (3.9+) and `match/case` for destructuring (3.10+).

2. **Hashability** is the contract for dict keys and set elements: constant `__hash__` + consistent `__eq__`. Immutable does not automatically mean hashable (e.g., a tuple containing a list).

3. **`defaultdict`** and **`__missing__`** eliminate boilerplate for handling missing keys. Prefer `setdefault` for simple cases.

4. **Subclass `UserDict`, not `dict`**, when building custom mappings. `UserDict` uses composition internally, avoiding subtle bugs from `dict`'s C-level shortcuts.

5. **`MappingProxyType`** gives you a read-only facade; **dictionary views** are lightweight and support set operations.

6. **Sets** are underused! `&`, `|`, `-`, `^` replace loops and conditionals. Membership testing is O(1).

7. **`Counter`** is a multiset. **`ChainMap`** layers mappings for scoped lookups. **`OrderedDict`** matters when key order affects equality.

### Concept Map

[[dict-comprehensions-unpacking-merging]] | [[pattern-matching-mappings]] | [[hashability]] | [[defaultdict-and-missing]] | [[dict-variations]] | [[immutable-mappings-and-views]] | [[set-theory-and-operations]]"""},
]

output_path = "/Users/olympus/projects/distill-tech-books/library/fluent-python/chapters/03-dictionaries-and-sets/chapter-03.ipynb"
build_notebook("Chapter 3: Dictionaries and Sets", cells, output_path)
print(f"Notebook created: {output_path}")
