import dataclasses
import typing

from .base import PyObject, TypeForm, Value
from .type import Type


class Callable(PyObject):
    "Any callable, have arguments & return types"
    name: str
    args: tuple[TypeForm, ...]
    returns: TypeForm
    type: typing.ClassVar[Type]

    def match_args(self, *values: PyObject) -> bool:
        return len(self.args) == len(values) and all(arg_type.match(value) for arg_type, value in zip(self.args, values))

    def apply(self, *args: PyObject) -> PyObject:
        return Value(type=self.returns)


@dataclasses.dataclass(frozen=True)
class Function(Callable):
    "A concrete function"
    name: str
    args: tuple[TypeForm, ...]
    returns: TypeForm


from . import definitions
del definitions
