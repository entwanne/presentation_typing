import ast
import collections.abc
import typing

from . import builtins, checker, error
from .context import Context, Cursor, new_layer
from .object import Value, PyObject, TypeForm, NoType, NoValue


class TypingVisitor(ast.NodeVisitor):
    'AST visitor to check types for assignments & operations'

    def __init__(self):
        self.contexts = {}
        self.context = None
        self.cursor = Cursor()

        self.errors = []

    @property
    def annotations(self) -> collections.abc.MutableMapping[str, TypeForm]:
        return self.context.annotations

    def add_error(self, error_type: type[error.BaseError], **kwargs: typing.Any) -> None:
        self.errors.append(error_type(**kwargs, cursor=self.cursor))

    # Entrypoints

    def visit_file(self, tree: ast.AST, filename: str) -> PyObject:
        self.contexts[filename] = Context(filename=filename)
        with new_layer(
                self,
                context=self.contexts[filename],
                cursor=self.cursor.replace(filename=filename),
        ):
            return self.visit(tree)

    def visit(self, node: ast.AST) -> PyObject:
        assert node is not None

        with new_layer(
                self,
                cursor=self.cursor.replace(
                    line=getattr(node, 'lineno', None),
                    col=getattr(node, 'col_offset', None),
                ),
        ):
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
