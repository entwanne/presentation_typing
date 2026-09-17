import dataclasses
import typing

if typing.TYPE_CHECKING:
    from .type import Type


class PyObject:
    "Any Python object, instance of object"
    type: TypeForm


class TypeForm(PyObject):
    "Any object representing a type or a type expression, can be used as an annotation"
    name: str
    type: typing.ClassVar[Type]

    def match(self, value: PyObject) -> bool:
        return value.type <= self

    def __le__(self, type: TypeForm) -> bool:
        return NotImplemented

    def __str__(self) -> str:
        return f'<Type:{self.name}>'


@dataclasses.dataclass(frozen=True)
class Value(PyObject):
    "A concrete value with a type"
    type: TypeForm


from . import definitions
del definitions
