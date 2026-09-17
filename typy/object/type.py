import dataclasses
import typing

from .base import TypeForm

if typing.TYPE_CHECKING:
    from .function import Callable


@dataclasses.dataclass(frozen=True)
class Type(TypeForm):
    "Concrete type with bases & methods"
    name: str
    bases: tuple[TypeForm, ...]
    methods: dict[str, Callable] = dataclasses.field(repr=False)

    def __le__(self, rhs: TypeForm) -> bool:
        if self.bases:
            return any(base <= rhs for base in self.bases)
        if isinstance(rhs, __class__):
            return self.name is rhs.name
        return NotImplemented

    def __ge__(self, rhs: TypeForm) -> bool:
        if self.bases:
            return any(base >= rhs for base in self.bases)
        if isinstance(rhs, __class__):
            return self.name is rhs.name
        return NotImplemented


@dataclasses.dataclass(frozen=True)
class UnionType(TypeForm):
    "Union of types, like int | str"
    types: tuple[TypeForm, ...]

    @classmethod
    def from_types(cls, *types: TypeForm) -> typing.Self:
        return cls(types)

    @property
    def name(self) -> str:
        return f'({" | ".join(t.name for t in self.types)})'

    def __or__(self, rhs: TypeForm) -> typing.Self:
        if isinstance(rhs, __class__):
            return __class__.from_types(*self.types, *rhs.types)
        else:
            return __class__.from_types(*self.types, rhs)

    def __ror__(self, lhs: TypeForm) -> typing.Self:
        # lhs is not an UnionType, otherwhise __or__ would have matched
        return __class__.from_types(lhs, *self.types)

    def __le__(self, type: TypeForm) -> bool:
        return any(subtype <= type for subtype in self.types)

    def __ge__(self, type: TypeForm) -> bool:
        return any(subtype >= type for subtype in self.types)
