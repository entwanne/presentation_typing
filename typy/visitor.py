import ast

from . import builtins, checker
from .object import Value, PyObject, TypeForm, NoType, NoValue


class TypingVisitor(ast.NodeVisitor):
    'AST visitor to check types for assignments & operations'

    def __init__(self):
        self.filename = None
        self.annotations = {}
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
        self.annotations.clear()
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

    def visit_BinOp(self, node: ast.BinOp) -> TypeForm:
        left = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(node.op, ast.BitOr) and isinstance(left, TypeForm) and isinstance(right, TypeForm):
            return left | right

        return NoType

    def visit_Name(self, node: ast.Name) -> PyObject:
        if hasattr(builtins, node.id):
            return getattr(builtins, node.id)
        self.add_error('Error', f'{node.id} type not found', node=node)
        return NoType

    def visit_Assign(self, node: ast.Assign) -> NoValue:
        for target in node.targets:
            checker.check_assign(self, target, node.value)
        return NoValue

    def visit_AnnAssign(self, node: ast.AnnAssign) -> NoValue:
        checker.check_assign(self, node.target, node.value, node.annotation)
        return NoValue
