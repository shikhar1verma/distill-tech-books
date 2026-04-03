"""Build the Chapter 5 notebook using notebook_builder.build_notebook()."""

import sys
sys.path.insert(0, "/Users/olympus/projects/distill-tech-books/src")
from notebook_builder import build_notebook

cells = [
    # ── Title ──
    {"type": "markdown", "content": "# Chapter 5: Data Class Builders\n\n**Fluent Python, 2nd Edition** -- Luciano Ramalho\n\nPython offers three shortcuts to build classes that are primarily collections of fields:\n- `collections.namedtuple` (since 2.6)\n- `typing.NamedTuple` (since 3.5, class syntax 3.6)\n- `@dataclasses.dataclass` (since 3.7)\n\nThis notebook distills each builder with runnable examples."},

    # ── Section 1: Overview ──
    {"type": "markdown", "content": "---\n## 1. Overview: The Boilerplate Problem\n\nA plain class with fields requires writing `__init__`, `__repr__`, and `__eq__` by hand.\nData class builders generate all of these automatically."},

    {"type": "code", "content": """# The problem: a plain class with no useful defaults
class Coordinate:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

moscow = Coordinate(55.76, 37.62)
location = Coordinate(55.76, 37.62)

print(f"repr:  {moscow!r}")
print(f"equal: {moscow == location}")  # compares object IDs, not values!
print(f"attrs: {(moscow.lat, moscow.lon) == (location.lat, location.lon)}")"""},

    {"type": "markdown", "content": "All three builders fix this. Here is the same class via each builder:"},

    {"type": "code", "content": """from collections import namedtuple
from typing import NamedTuple
from dataclasses import dataclass

# 1) collections.namedtuple
CoordNT = namedtuple('CoordNT', 'lat lon')

# 2) typing.NamedTuple
class CoordTyped(NamedTuple):
    lat: float
    lon: float

# 3) @dataclass
@dataclass(frozen=True)
class CoordDC:
    lat: float
    lon: float

# All three give useful repr and value-based equality
for cls in [CoordNT, CoordTyped, CoordDC]:
    a = cls(55.76, 37.62)
    b = cls(55.76, 37.62)
    print(f"{cls.__name__:12s}  repr={a!r:45s}  eq={a == b}")"""},

    {"type": "markdown", "content": "### Feature comparison table\n\n| Feature | `namedtuple` | `NamedTuple` | `@dataclass` |\n|---|---|---|---|\n| Mutable instances | No | No | Yes (default) |\n| Class statement syntax | No | Yes | Yes |\n| Construct dict | `x._asdict()` | `x._asdict()` | `dataclasses.asdict(x)` |\n| Get field names | `x._fields` | `x._fields` | `[f.name for f in fields(x)]` |\n| New instance w/ changes | `x._replace(...)` | `x._replace(...)` | `dataclasses.replace(x, ...)` |\n| Build class at runtime | `namedtuple(...)` | `NamedTuple(...)` | `make_dataclass(...)` |"},

    # ── Section 2: Classic Named Tuples ──
    {"type": "markdown", "content": "---\n## 2. Classic Named Tuples (`collections.namedtuple`)"},

    {"type": "code", "content": """from collections import namedtuple

# Define a named tuple
City = namedtuple('City', 'name country population coordinates')
tokyo = City('Tokyo', 'JP', 36.933, (35.689722, 139.691667))

print(f"repr:        {tokyo}")
print(f"population:  {tokyo.population}")
print(f"by index:    {tokyo[1]}")
print(f"is tuple:    {isinstance(tokyo, tuple)}")"""},

    {"type": "code", "content": """# Key attributes and methods: _fields, _make, _asdict, _field_defaults

print("_fields:", City._fields)

CoordNT = namedtuple('CoordNT', 'lat lon')
delhi_data = ('Delhi NCR', 'IN', 21.935, CoordNT(28.613889, 77.208889))
delhi = City._make(delhi_data)   # build from iterable
print("_make:  ", delhi)
print("_asdict:", delhi._asdict())"""},

    {"type": "code", "content": """# Defaults (Python 3.7+): applied to the N rightmost fields
CoordWithRef = namedtuple('CoordWithRef', 'lat lon reference', defaults=['WGS84'])

print(CoordWithRef(0, 0))
print("_field_defaults:", CoordWithRef._field_defaults)"""},

    # ── Section 3: Typed Named Tuples ──
    {"type": "markdown", "content": "---\n## 3. Typed Named Tuples (`typing.NamedTuple`)\n\nAdds type annotations + class-body syntax. Still produces an immutable tuple subclass."},

    {"type": "code", "content": """from typing import NamedTuple

class Coordinate(NamedTuple):
    lat: float
    lon: float
    reference: str = 'WGS84'

    def __str__(self):
        ns = 'N' if self.lat >= 0 else 'S'
        we = 'E' if self.lon >= 0 else 'W'
        return f'{abs(self.lat):.1f} {ns}, {abs(self.lon):.1f} {we}'

pt = Coordinate(55.76, 37.62)
print(f"repr: {pt!r}")
print(f"str:  {pt}")
print(f"type annotations: {Coordinate.__annotations__}")
print(f"is tuple subclass: {issubclass(Coordinate, tuple)}")
print(f"is NamedTuple subclass: {issubclass(Coordinate, NamedTuple)}")  # False!"""},

    {"type": "markdown", "content": "> **Key insight:** `typing.NamedTuple` appears as a superclass in the class statement,\n> but it is *not* an actual base class. The metaclass machinery builds the class as a\n> `tuple` subclass. `issubclass(Coordinate, NamedTuple)` is `False`."},

    # ── Section 4: Type Hints 101 ──
    {"type": "markdown", "content": "---\n## 4. Type Hints 101\n\nType hints have **no runtime effect**. Python reads them at import time to build\n`__annotations__`, but never enforces them. Only external tools (Mypy, Pyright) check types."},

    {"type": "code", "content": """from typing import NamedTuple

class Coordinate(NamedTuple):
    lat: float
    lon: float

# Python happily accepts wrong types at runtime!
trash = Coordinate('Ni!', None)
print(f"No error: {trash}")  # Coordinate(lat='Ni!', lon=None)"""},

    {"type": "code", "content": """# How annotations behave in a plain class vs NamedTuple vs dataclass

class DemoPlain:
    a: int           # annotation only -- no class attribute created
    b: float = 1.1   # annotation + class attribute
    c = 'spam'       # class attribute, NO annotation

print("Plain __annotations__:", DemoPlain.__annotations__)
print("Plain has 'a'?", hasattr(DemoPlain, 'a'))   # False!
print("Plain.b:", DemoPlain.b)
print("Plain.c:", DemoPlain.c)"""},

    {"type": "code", "content": """from typing import NamedTuple
from dataclasses import dataclass

class DemoNT(NamedTuple):
    a: int
    b: float = 1.1
    c = 'spam'       # plain class attr, not a field

@dataclass
class DemoDC:
    a: int
    b: float = 1.1
    c = 'spam'       # plain class attr, not a field

# Both have annotations for a and b (not c)
print("NT annotations:", DemoNT.__annotations__)
print("DC annotations:", DemoDC.__annotations__)

# NamedTuple creates descriptors; dataclass does not
print("\\nNT.a type:", type(DemoNT.a).__name__)  # _tuplegetter descriptor
print("DC has class-level 'a'?", hasattr(DemoDC, 'a'))  # False (only on instances)

# Instances behave as expected
nt = DemoNT(8)
dc = DemoDC(9)
print(f"\\nnt.a={nt.a}, nt.b={nt.b}, nt.c={nt.c}")
print(f"dc.a={dc.a}, dc.b={dc.b}, dc.c={dc.c}")"""},

    # ── Section 5: @dataclass Decorator ──
    {"type": "markdown", "content": "---\n## 5. `@dataclass` Decorator and Field Options\n\n```python\n@dataclass(*, init=True, repr=True, eq=True, order=False,\n           unsafe_hash=False, frozen=False)\n```\n\nMost useful changes from defaults:\n- `frozen=True` -- immutable instances (also enables hashing)\n- `order=True` -- generate `__lt__`, `__le__`, `__gt__`, `__ge__`"},

    {"type": "code", "content": """from dataclasses import dataclass, field, fields, asdict, replace

@dataclass(frozen=True, order=True)
class Coordinate:
    lat: float
    lon: float

a = Coordinate(55.76, 37.62)
b = Coordinate(40.71, -74.01)

print(f"repr:    {a}")
print(f"eq:      {a == Coordinate(55.76, 37.62)}")
print(f"order:   {sorted([a, b])}")
print(f"hash:    {hash(a)}")   # works because frozen=True
print(f"asdict:  {asdict(a)}")
print(f"replace: {replace(a, lon=0.0)}")"""},

    {"type": "code", "content": """# field() function: control per-field behavior
# Key options: default, default_factory, repr, compare, hash, metadata

from dataclasses import dataclass, field

@dataclass
class ClubMember:
    name: str
    guests: list[str] = field(default_factory=list)  # MUST use default_factory for mutable defaults
    athlete: bool = field(default=False, repr=False)  # hidden from repr

m1 = ClubMember('Alice')
m2 = ClubMember('Bob', ['Charlie'])
m1.guests.append('Dave')

print(m1)  # athlete not shown
print(m2)
print(f"m1 guests: {m1.guests}")
print(f"m2 guests: {m2.guests}")  # each instance has its own list"""},

    {"type": "code", "content": """# What happens if you try a mutable default directly?
from dataclasses import dataclass

try:
    @dataclass
    class BadClub:
        name: str
        guests: list = []  # BAD -- @dataclass rejects this
except ValueError as e:
    print(f"ValueError: {e}")"""},

    {"type": "code", "content": """# fields() introspection
from dataclasses import dataclass, field, fields

@dataclass
class ClubMember:
    name: str
    guests: list[str] = field(default_factory=list)
    athlete: bool = field(default=False, repr=False)

for f in fields(ClubMember):
    print(f"  {f.name:10s}  default={str(f.default):20s}  repr={f.repr}")"""},

    # ── Section 6: Post-init ──
    {"type": "markdown", "content": "---\n## 6. Post-init Processing and Advanced Features\n\n`__post_init__` is called by the generated `__init__` as its last step.\nUse it for validation and computed fields."},

    {"type": "code", "content": """from dataclasses import dataclass, field

@dataclass
class ClubMember:
    name: str
    guests: list[str] = field(default_factory=list)

@dataclass
class HackerClubMember(ClubMember):
    all_handles: set = field(default_factory=set, init=False, repr=False)  # class-level workaround
    handle: str = ''

    def __post_init__(self):
        if self.handle == '':
            self.handle = self.name.split()[0]
        # Note: in the book, all_handles is a ClassVar shared across instances.
        # Here we demonstrate __post_init__ mechanics with a simple validation.
        if not self.handle.isidentifier():
            raise ValueError(f"handle {self.handle!r} is not a valid identifier")

anna = HackerClubMember('Anna Ravenscroft', handle='AnnaRaven')
leo = HackerClubMember('Leo Rochael')

print(anna)
print(leo)   # handle auto-set to 'Leo'

try:
    bad = HackerClubMember('123 Bad', handle='123bad')
except ValueError as e:
    print(f"Validation caught: {e}")"""},

    {"type": "code", "content": """# typing.ClassVar -- exclude from field generation
# dataclasses.InitVar -- pass to __post_init__ but don't store

from dataclasses import dataclass, field, InitVar
from typing import ClassVar

@dataclass
class DatabaseRecord:
    identifier: str
    title: str = '<untitled>'
    _registry: ClassVar[dict[str, 'DatabaseRecord']] = {}   # class-level, not a field
    database: InitVar[dict | None] = None                    # init-only, not stored

    def __post_init__(self, database):
        if database is not None and self.title == '<untitled>':
            self.title = database.get(self.identifier, '<untitled>')
        DatabaseRecord._registry[self.identifier] = self

# Simulate a database lookup
fake_db = {'ABC-123': 'Fluent Python'}
rec = DatabaseRecord('ABC-123', database=fake_db)

print(f"title resolved: {rec.title}")
print(f"has 'database' attr? {hasattr(rec, 'database')}")  # False -- InitVar
print(f"registry: {DatabaseRecord._registry}")"""},

    # ── Section 7: Code Smell ──
    {"type": "markdown", "content": "---\n## 7. Data Class as Code Smell vs Scaffolding\n\n> *Data classes are like children. They are okay as a starting point, but to participate\n> as a grownup object, they need to take some responsibility.*\n> -- Martin Fowler & Kent Beck\n\n**Code smell:** A class with only data and no behavior suggests logic is misplaced elsewhere.\n\n**When data classes ARE appropriate:**\n1. **Scaffolding** -- quick start during early development, add behavior later\n2. **Intermediate representation** -- records for JSON import/export at system boundaries\n\nThe key question: *what behavior should live in this class?*"},

    {"type": "code", "content": """# Example: evolving a data class from scaffolding to a real class
from dataclasses import dataclass, field
from datetime import date
from enum import Enum, auto

class ResourceType(Enum):
    BOOK = auto()
    EBOOK = auto()
    VIDEO = auto()

@dataclass
class Resource:
    \"\"\"Media resource description (Dublin Core inspired).\"\"\"
    identifier: str
    title: str = '<untitled>'
    creators: list[str] = field(default_factory=list)
    date: date | None = None
    type: ResourceType = ResourceType.BOOK
    description: str = ''
    language: str = ''
    subjects: list[str] = field(default_factory=list)

    # Adding behavior turns this from a "code smell" into a real class
    def citation(self) -> str:
        authors = ', '.join(self.creators) if self.creators else 'Unknown'
        year = self.date.year if self.date else 'n.d.'
        return f'{authors} ({year}). {self.title}.'

book = Resource(
    '978-0-13-475759-9',
    'Refactoring, 2nd Edition',
    ['Martin Fowler', 'Kent Beck'],
    date(2018, 11, 19),
    ResourceType.BOOK,
    'Improving the design of existing code',
    'EN',
    ['computer programming', 'OOP'],
)
print(book.citation())
print(f"\\nAll fields:")
from dataclasses import fields as dc_fields
for f in dc_fields(book):
    print(f"  {f.name}: {getattr(book, f.name)!r}")"""},

    # ── Section 8: Pattern Matching ──
    {"type": "markdown", "content": "---\n## 8. Pattern Matching Class Instances (Python 3.10+)\n\nThree variations of class patterns:\n1. **Simple** -- `float(x)` (only for 9 blessed built-ins)\n2. **Keyword** -- `City(continent='Asia')`\n3. **Positional** -- `City('Asia')` (uses `__match_args__`)"},

    {"type": "code", "content": """from typing import NamedTuple

class City(NamedTuple):
    continent: str
    name: str
    country: str

cities = [
    City('Asia', 'Tokyo', 'JP'),
    City('Asia', 'Delhi', 'IN'),
    City('North America', 'Mexico City', 'MX'),
    City('North America', 'New York', 'US'),
    City('South America', 'Sao Paulo', 'BR'),
]

# Keyword class patterns
def match_asian_cities():
    results = []
    for city in cities:
        match city:
            case City(continent='Asia'):
                results.append(city)
    return results

# Positional class patterns (uses __match_args__)
def match_asian_countries_pos():
    results = []
    for city in cities:
        match city:
            case City('Asia', _, country):
                results.append(country)
    return results

print("Asian cities (keyword):", match_asian_cities())
print("Asian countries (positional):", match_asian_countries_pos())
print(f"\\n__match_args__: {City.__match_args__}")"""},

    {"type": "code", "content": """# Simple class patterns -- special syntax for 9 blessed built-in types
# bytes, dict, float, frozenset, int, list, set, str, tuple
# For these types, the argument captures the subject:

def classify(value):
    match value:
        case int(n):
            return f"integer: {n}"
        case float(x):
            return f"float: {x}"
        case str(s):
            return f"string: {s!r}"
        case _:
            return f"other: {value!r}"

for v in [42, 3.14, "hello", [1, 2]]:
    print(classify(v))"""},

    {"type": "code", "content": """# GOTCHA: case float: (without parens) matches ANYTHING and binds it
# case float():  -- correct, checks isinstance
# case float:    -- WRONG, just assigns to a variable named 'float'

x = 42
match x:
    case float():
        print("It's a float")
    case int():
        print("It's an int")    # This matches
    case _:
        print("Something else")"""},

    # ── Exercises ──
    {"type": "markdown", "content": "---\n## Exercises\n\nTest your understanding of data class builders."},

    {"type": "markdown", "content": "### Exercise 1: Named Tuple Design\n\nCreate a `Book` named tuple with fields: `title`, `author`, `year`, `isbn`.\n- Give `isbn` a default of `''`.\n- Create two instances and demonstrate `_asdict()`, `_replace()`, and `_fields`."},

    {"type": "code", "content": """# Exercise 1 -- try it yourself, then check below
from collections import namedtuple

Book = namedtuple('Book', 'title author year isbn', defaults=[''])

b1 = Book('Fluent Python', 'Luciano Ramalho', 2022, '978-1-492-05635-5')
b2 = Book('Refactoring', 'Martin Fowler', 2018)

print("b1:", b1)
print("b2:", b2)
print("b1._asdict():", b1._asdict())
print("b1._replace(year=2025):", b1._replace(year=2025))
print("Book._fields:", Book._fields)"""},

    {"type": "markdown", "content": "### Exercise 2: @dataclass with Validation\n\nCreate a `Temperature` dataclass with a `celsius` field. In `__post_init__`,\nraise `ValueError` if the temperature is below absolute zero (-273.15)."},

    {"type": "code", "content": """# Exercise 2 -- try it yourself, then check below
from dataclasses import dataclass

@dataclass
class Temperature:
    celsius: float

    def __post_init__(self):
        if self.celsius < -273.15:
            raise ValueError(f"{self.celsius} C is below absolute zero")

    @property
    def fahrenheit(self) -> float:
        return self.celsius * 9 / 5 + 32

    @property
    def kelvin(self) -> float:
        return self.celsius + 273.15

t = Temperature(100)
print(f"{t.celsius} C = {t.fahrenheit} F = {t.kelvin} K")

try:
    bad = Temperature(-300)
except ValueError as e:
    print(f"Caught: {e}")"""},

    {"type": "markdown", "content": "### Exercise 3: Pattern Matching\n\nGiven a list of shapes represented as dataclasses, use match/case to compute areas."},

    {"type": "code", "content": """# Exercise 3
from dataclasses import dataclass
import math

@dataclass
class Circle:
    radius: float

@dataclass
class Rectangle:
    width: float
    height: float

@dataclass
class Triangle:
    base: float
    height: float

shapes = [Circle(5), Rectangle(3, 4), Triangle(6, 8), Circle(1)]

for shape in shapes:
    match shape:
        case Circle(radius=r):
            area = math.pi * r ** 2
        case Rectangle(width=w, height=h):
            area = w * h
        case Triangle(base=b, height=h):
            area = 0.5 * b * h
    print(f"{shape!r:35s} -> area = {area:.2f}")"""},

    {"type": "markdown", "content": "---\n## Key Takeaways\n\n1. **Three builders, one goal:** eliminate `__init__`/`__repr__`/`__eq__` boilerplate\n2. **namedtuple** -- simplest, immutable tuple subclass, no type hints required\n3. **NamedTuple** -- adds type hints + class syntax, still immutable tuple\n4. **@dataclass** -- most flexible (mutable by default, field options, `__post_init__`)\n5. **Type hints are not enforced at runtime** -- use Mypy/Pyright for static checking\n6. **Use `field(default_factory=list)`** instead of mutable defaults\n7. **Data classes with no behavior are a code smell** -- add methods or treat as scaffolding\n8. **`__match_args__`** is auto-generated, enabling positional pattern matching"},
]

output_path = "/Users/olympus/projects/distill-tech-books/library/fluent-python/chapters/05-data-class-builders/chapter-05-data-class-builders.ipynb"
build_notebook("Chapter 5: Data Class Builders", cells, output_path)
print(f"Notebook created: {output_path}")
