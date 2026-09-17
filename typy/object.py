import dataclasses
import typing


# Bases

class PyObject:
    "Any Python object, instance of object"
    type: Type


@dataclasses.dataclass(frozen=True)
class Type(PyObject):
    "Any object representing a type or a type expression, can be used as an annotation"
    name: str
    type: typing.ClassVar[Type]

    def match(self, value: PyObject) -> bool:
        return value.type is self

    def __str__(self) -> str:
        return f'<Type:{self.name}>'


@dataclasses.dataclass(frozen=True)
class Value(PyObject):
    "A concrete value with a type"
    type: Type


# Definition of `type` metaclass
base_type = Type(name='type')
# Set it as the type of types
Type.type = base_type

NoType = Type('NoType')
NoValue = Value(type=NoType)
