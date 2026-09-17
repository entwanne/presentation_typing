import dataclasses

from .base import TypeForm


@dataclasses.dataclass(frozen=True)
class Type(TypeForm):
    "Concrete type"
    name: str

    def __le__(self, rhs: TypeForm) -> bool:
        if isinstance(rhs, __class__):
            return self.name is rhs.name
        return NotImplemented

    def __ge__(self, rhs: TypeForm) -> bool:
        if isinstance(rhs, __class__):
            return self.name is rhs.name
        return NotImplemented
