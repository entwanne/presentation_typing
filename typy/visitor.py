import ast

from . import builtins
from .object import Value, PyObject, Type, NoType, NoValue


class TypingVisitor(ast.NodeVisitor):
    'AST visitor to check types for assignments & operations'

    def __init__(self):
        self.filename = None
        self.errors = []

    def add_error(self, title: str, error: str, node=None) -> None:
        parts = [title]
        if self.filename:
            parts.append(f' on {self.filename}')
            if node:
                parts.append(f'::{node.lineno}')
        parts.append(f': {error}')
        self.errors.append(''.join(parts))

    # Entrypoints

    def visit_file(self, node: ast.AST, filename: str) -> PyObject:
        self.filename = filename
        return self.visit(node)

    def visit(self, node: ast.AST) -> PyObject:
        assert node is not None

        value = super().visit(node)
        if not isinstance(value, PyObject):
            raise ValueError(f'Visit call returned a value of type {type(value).__qualname__} for node {type(node).__qualname__} which is not a PyObject')
        return value

    # Node visit methods

    def generic_visit(self, node: ast.AST) -> NoValue:
        super().generic_visit(node)
        return NoValue

    def visit_Constant(self, node: ast.Constant) -> Value:
        return Value(type=getattr(builtins, type(node.value).__name__))

    def visit_Name(self, node: ast.Name) -> PyObject:
        if hasattr(builtins, node.id):
            return getattr(builtins, node.id)
        self.add_error('Error', f'{node.id} type not found', node=node)
        return NoType

    def visit_AnnAssign(self, node: ast.AnnAssign) -> NoValue:
        if node.value is None:
            return

        value = self.visit(node.value)
        if value is NoValue:
            return NoValue

        annotation = self.visit(node.annotation)
        if not isinstance(annotation, Type):
            self.add_error('Error', f'{annotation!r} is not a type', node=node.annotation)
            return NoValue

        if not annotation.match(value):
            self.add_error('Assignment error', f'Trying to assign value of type {value.type.name} to variable {node.target.id} annotated with {annotation.name}', node=node.target)

        return NoValue
