import dataclasses
from typing import ClassVar

from .context import Cursor
from .object import TypeForm


@dataclasses.dataclass(frozen=True)
class BaseError:
    cursor: Cursor

    title: ClassVar[str] = 'Error'

    @property
    def location(self) -> str:
        return str(self.cursor)

    def __str__(self) -> str:
        message = getattr(self, 'message', '')
        if location := self.location:
            return f'{self.title} on {location}: {message}'
        return f'{self.title}: {message}'


@dataclasses.dataclass(frozen=True)
class Error(BaseError):
    message: str


@dataclasses.dataclass(frozen=True)
class AssignmentError(BaseError):
    dest: str
    annotation: TypeForm
    type: TypeForm

    title: ClassVar[str] = 'Assignment error'

    @property
    def message(self) -> str:
        return f'Trying to assign value of type {self.type.name} to variable {self.dest} annotated with {self.annotation.name}'


@dataclasses.dataclass(frozen=True)
class ExpressionError(BaseError):
    operation: str
    values: tuple

    title: ClassVar[str] = 'Expression error'

    @property
    def message(self) -> str:
        types = tuple(value.type.name if value else 'None' for value in self.values)
        match types:
            case ():
                return f'Incompatible operation {self.operation}'
            case (t,):
                return f'Incompatible operation {self.operation} for value of type {t}'
            case (*left, right):
                return f'Incompatible operation {self.operation} for values of types {", ".join(left)} and {right}'
        return ''


@dataclasses.dataclass(frozen=True)
class CallError(BaseError):
    function: str
    args: tuple

    title: ClassVar[str] = 'Call error'

    @property
    def message(self) -> str:
        return f'cannot call {self.function} with arg types {", ".join(arg.type.name for arg in self.args)}'
