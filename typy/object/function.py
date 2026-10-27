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

    def bind(self, value: PyObject) -> Method:
        return Method(function=self, value=value)


@dataclasses.dataclass(frozen=True)
class Function(Callable):
    "A concrete function"
    name: str
    args: tuple[TypeForm, ...]
    returns: TypeForm


@dataclasses.dataclass(frozen=True)
class Method(Callable):
    "Function bounded to a value"
    function: Callable
    value: PyObject

    @property
    def name(self) -> str:
        return self.function.name

    @property
    def args(self) -> tuple[TypeForm, ...]:
        self_arg, *args = self.function.args
        assert self_arg is self.value.type
        return tuple(args)

    @property
    def returns(self) -> TypeForm:
        return self.function.returns

    def apply(self, *values: PyObject) -> PyObject:
        return self.function.apply(self.value, *values)


from . import definitions
del definitions
