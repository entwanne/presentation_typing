import collections.abc
import dataclasses

from .base import PyObject, TypeForm
from .function import Callable, Function, Method


@dataclasses.dataclass(frozen=True)
class ApplicationFunction(Function):
    "Function with a custom application to call"
    apply: collections.abc.Callable[..., PyObject]


@dataclasses.dataclass(frozen=True)
class DynamicFunction(Callable):
    "Kind of function with dynamic properties to evaluate args & return annotations and function application"
    dynamic: collections.abc.Callable[[PyObject | None], Callable]

    @property
    def name(self):
        return self.dynamic(None).name

    @property
    def args(self) -> tuple[TypeForm, ...]:
        return self.dynamic(None).args

    @property
    def returns(self) -> TypeForm:
        return self.dynamic(None).returns

    def apply(self, *args: PyObject) -> PyObject:
        return self.dynamic(None).apply(*args)

    def bind(self, value: PyObject) -> DynamicMethod:
        return DynamicMethod(function=self, value=value)


class DynamicMethod(Method):
    "Method linked to a dynamic function"
    function: DynamicFunction

    @property
    def args(self) -> tuple[TypeForm, ...]:
        return self.function.dynamic(self.value).args

    @property
    def returns(self) -> TypeForm:
        return self.function.dynamic(self.value).returns
