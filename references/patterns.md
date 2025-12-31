# Common Fix Patterns

## Table of Contents

1. [Layer 1: Quick Wins](#layer-1-quick-wins)
2. [Layer 2: Annotation Completeness](#layer-2-annotation-completeness)
3. [Layer 3: Type Safety](#layer-3-type-safety)
4. [Layer 4: Structural Patterns](#layer-4-structural-patterns)
5. [Layer 5: External Dependencies](#layer-5-external-dependencies)
6. [Layer 6: Edge Cases](#layer-6-edge-cases)

---

## Layer 1: Quick Wins

### Unused Imports

```python
# Before
from typing import List, Dict, Optional  # Optional unused

# After
from typing import List, Dict
```

### Missing Return Types

```python
# Before
def get_name(user):
    return user.name

# After
def get_name(user: User) -> str:
    return user.name
```

### Generic Type Arguments

```python
# Before
def get_items() -> List:
    return []

# After
def get_items() -> List[Item]:
    return []
```

### Dict/List Literal Types

```python
# Before
config = {}  # type: dict

# After  
config: Dict[str, str] = {}
```

---

## Layer 2: Annotation Completeness

### Function Parameters

```python
# Before
def process(data, options=None):
    ...

# After
def process(data: bytes, options: Options | None = None) -> Result:
    ...
```

### Class Attributes

```python
# Before
class User:
    def __init__(self, name):
        self.name = name
        self.created_at = None

# After
class User:
    name: str
    created_at: datetime | None
    
    def __init__(self, name: str) -> None:
        self.name = name
        self.created_at = None
```

### Module Variables

```python
# Before
DEFAULT_TIMEOUT = 30
_cache = {}

# After
DEFAULT_TIMEOUT: int = 30
_cache: Dict[str, CacheEntry] = {}
```

---

## Layer 3: Type Safety

### None Checks (Optional Handling)

```python
# Before - pyright error: "x" may be None
def process(x: str | None) -> str:
    return x.upper()

# After - Option 1: Early return
def process(x: str | None) -> str:
    if x is None:
        return ""
    return x.upper()

# After - Option 2: Default
def process(x: str | None) -> str:
    return (x or "").upper()

# After - Option 3: Raise
def process(x: str | None) -> str:
    if x is None:
        raise ValueError("x is required")
    return x.upper()
```

### Type Narrowing with isinstance()

```python
# Before
def handle(value: str | int) -> str:
    return value.upper()  # Error: int has no upper()

# After
def handle(value: str | int) -> str:
    if isinstance(value, str):
        return value.upper()
    return str(value)
```

### TypeGuard for Complex Narrowing

```python
from typing import TypeGuard

def is_string_list(val: list) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(items: list) -> None:
    if is_string_list(items):
        # items is now list[str]
        for s in items:
            print(s.upper())
```

### Union Type Handling

```python
# Before
def get_value(data: dict | list) -> Any:
    if isinstance(data, dict):
        return data.get("value")
    return data[0]

# After
def get_value(data: dict[str, int] | list[int]) -> int | None:
    if isinstance(data, dict):
        return data.get("value")
    return data[0] if data else None
```

---

## Layer 4: Structural Patterns

### Conditional Imports (try/except)

```python
# Before - creates type union issues
try:
    from fast_lib import process
except ImportError:
    def process(x):  # Different signature
        return slow_process(x)

# After - Option 1: Import at TYPE_CHECKING only
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fast_lib import process as _process

try:
    from fast_lib import process
except ImportError:
    from slow_lib import process

# After - Option 2: Consistent signatures
from typing import Callable

process: Callable[[bytes], Result]

try:
    from fast_lib import process
except ImportError:
    from slow_lib import process
```

### TypedDict for Dict Shapes

```python
# Before
def get_user() -> dict:
    return {"name": "Alice", "age": 30}

# After
from typing import TypedDict

class User(TypedDict):
    name: str
    age: int

def get_user() -> User:
    return {"name": "Alice", "age": 30}

# With optional keys
class UserPartial(TypedDict, total=False):
    name: str
    age: int
    email: str  # Optional
```

### Protocol for Duck Typing

```python
# Before - accepts any object with read()
def process(file):
    return file.read()

# After
from typing import Protocol

class Readable(Protocol):
    def read(self) -> bytes: ...

def process(file: Readable) -> bytes:
    return file.read()
```

### Dataclasses with Defaults

```python
# Before - mutable default
@dataclass
class Config:
    items: list = []  # Bug: shared mutable default

# After
from dataclasses import dataclass, field

@dataclass
class Config:
    items: list[str] = field(default_factory=list)
```

---

## Layer 5: External Dependencies

### Installing Type Stubs

```bash
# Common stub packages
pip install types-requests
pip install types-PyYAML
pip install types-python-dateutil
pip install types-redis

# Find stubs
pip search types-{package}
```

### Inline Stubs for Untyped Libraries

```python
# stubs/untyped_lib.pyi
def some_function(arg: str) -> int: ...

class SomeClass:
    def method(self, x: int) -> str: ...
```

Add to pyrightconfig.json:
```json
{
  "stubPath": "stubs"
}
```

### Minimal Workarounds

When stubs don't exist and you can't create them:

```python
# Document in typing-findings.md, then:
from untyped_lib import thing  # type: ignore[import]  # See typing-findings.md#untyped-lib
```

---

## Layer 6: Edge Cases

### Complex Generics

```python
# Bounded TypeVar
from typing import TypeVar

T = TypeVar("T", bound="BaseModel")

def clone(obj: T) -> T:
    return obj.copy()

# Covariant/Contravariant
from typing import Generic, TypeVar

T_co = TypeVar("T_co", covariant=True)

class Reader(Generic[T_co]):
    def read(self) -> T_co: ...
```

### Overloaded Functions

```python
from typing import overload

@overload
def get(key: str) -> str: ...
@overload
def get(key: str, default: int) -> str | int: ...

def get(key: str, default: int | None = None) -> str | int:
    ...
```

### Metaprogramming

For dynamically generated classes/methods, document limitations:

```python
# This class is generated at runtime by metaclass
# Type stubs in stubs/generated.pyi provide annotations
from generated import DynamicClass  # type: ignore[import]
```

### Callbacks and Callables

```python
from typing import Callable

# Function that takes a callback
def on_complete(callback: Callable[[int, str], None]) -> None:
    callback(42, "done")

# With optional args
from typing import Protocol

class Handler(Protocol):
    def __call__(self, code: int, message: str = ...) -> None: ...

def on_complete(handler: Handler) -> None:
    handler(42)
```
