import collections.abc
import dataclasses
import typing
from collections import ChainMap
from contextlib import contextmanager

from .object import PyObject, TypeForm


@dataclasses.dataclass(frozen=True)
class Cursor:
    filename: str | None = None
    line: int | None = None
    col: int | None = None

    def replace(self, **kwargs: typing.Any) -> typing.Self:
        return dataclasses.replace(
            self,
            **{
                key: value
                for key, value in kwargs.items()
                if value is not None
            },
        )

    def __str__(self) -> str:
        if self.filename is not None:
            if self.line is not None:
                return f'{self.filename}::{self.line}'
            return self.filename
        return ''


@dataclasses.dataclass(frozen=True)
class Context:
    filename: str
    namespace: ChainMap[str, PyObject] = dataclasses.field(default_factory=ChainMap)
    annotations: ChainMap[str, TypeForm] = dataclasses.field(default_factory=ChainMap)

    def new_child(self) -> typing.Self:
        return dataclasses.replace(
            self,
            namespace=self.namespace.new_child(),
            annotations=self.annotations.new_child(),
        )

    @property
    def parents(self) -> typing.Self:
        return dataclasses.replace(
            self,
            namespace=self.namespace.parents,
            annotations=self.annotations.parents,
        )

    @property
    def last(self) -> typing.Self:
        return dataclasses.replace(
            self,
            namespace=ChainMap(self.namespace.maps[0]),
            annotations=ChainMap(self.annotations.maps[0]),
        )


@contextmanager
def new_layer(obj: typing.Any, **kwargs: typing.Any) -> collections.abc.Generator[None]:
    old = {key: getattr(obj, key) for key in kwargs}
    try:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        yield
    finally:
        for key, value in old.items():
            setattr(obj, key, value)
