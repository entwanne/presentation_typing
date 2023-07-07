# All by mypy

## All by mypy

- Mypy is the standard Python type checker
- That supports almost all Python typing features
- That makes Python+mypy a statically typed language

---

- It accepts structural typing
- It uses type inference in typed contexts


## All by mypy

- Mypy recognizes complex types such as collections or protocols

---

- Then prefer `Iterable` over `list` for expected arguments when you don't necessarily need a list
- Note that SQLalchemy query results are iterables (but not lists)


## All by mypy

- Protocols are used to define what is expected for an interface

```python
from typing import Protocol

class PayoutProtocol(Protocol):
    external_id: str
    amount: int
```

---

- This will recognize all object types that define these attributes
- Without needing to inherit from the protocol class (structural typing)
- And the class can embed other attributes

```python
import dataclasses

@dataclasses.dataclass
class Payout:
    id: int
    external_id: str
    amount: int
```

---

- Unfortunately they don't work well with SQLAlchemy models (because of mapped attributes)


## All by mypy

- Protocols can also be checked dynamically
- But need to be explicitly defined for that

```python
from typing import runtime_checkable

@runtime_checkable
class PayoutProtocol(Protocol):
    external_id: str
    amount: int
```

---

```pycon
>>> isinstance(Payout(id=1, external_id='test', amount=100), PayoutProtocol)
```


## All by mypy

- Mypy includes a compiler, `mypyc`, that benefits from type hints to make optimizations
