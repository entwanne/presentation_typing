import functools
import typing

from .base import PyObject, TypeForm


class _NoType(TypeForm):
    @functools.cache # type: ignore
    def __new__(cls) -> typing.Self:
        return super().__new__(cls)

    @property
    def name(self) -> str:
        return '<NoType>'

    def __le__(self, rhs: TypeForm) -> bool:
        return False

    def __ge__(self, lhs: TypeForm) -> bool:
        return False


class _NoValue(PyObject):
    @functools.cache # type: ignore
    def __new__(cls) -> typing.Self:
        return super().__new__(cls)

    @property
    def type(self) -> TypeForm:
        return NoType

    def __repr__(self) -> str:
        return '<NoValue>'


NoType = _NoType()
NoValue = _NoValue()
