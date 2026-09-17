import ast
import collections.abc
import typing

from . import builtins, checker, error
from .context import Context, Cursor, new_layer
from .object import Callable, Value, Function, PyObject, Type, TypeForm, NoType, NoValue


class TypingVisitor(ast.NodeVisitor):
    'AST visitor to check types for assignments & operations'

    def __init__(self):
        self.contexts = {}
        self.context = None
        self.cursor = Cursor()

        self.errors = []

    @property
    def namespace(self) -> collections.abc.MutableMapping[str, PyObject]:
        return self.context.namespace

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

    def visit_BinOp(self, node: ast.BinOp) -> PyObject:
        left = self.visit(node.left)
        right = self.visit(node.right)
        return checker.check_operation(
            self,
            type(node.op),
            (left, right),
            error_args={
                'error_type': error.ExpressionError,
                'operation': type(node.op).__name__,
                'values': (left, right),
            }
        )

    def visit_Name(self, node: ast.Name) -> PyObject:
        if node.id in self.namespace:
            return self.namespace[node.id]
        if hasattr(builtins, node.id):
            return getattr(builtins, node.id)
        self.add_error(error.Error, message=f'{node.id} variable not found')
        return NoValue

    def visit_Call(self, node: ast.Call) -> PyObject:
        func = self.visit(node.func)
        args = tuple(self.visit(arg) for arg in node.args)
        return checker.check_operation(
            self,
            ast.Call,
            (func, *args),
            error_args={
                'error_type': error.CallError,
                'function': func.name if isinstance(func, Callable) else '',
                'args': args,
            }
        )

    def visit_Assign(self, node: ast.Assign) -> NoValue:
        for target in node.targets:
            checker.check_assign(self, target, node.value)
        return NoValue

    def visit_AnnAssign(self, node: ast.AnnAssign) -> NoValue:
        checker.check_assign(self, node.target, node.value, node.annotation)
        return NoValue

    def visit_FunctionDef(self, node: ast.FunctionDef) -> NoValue:
        self.namespace[node.name] = Function(
            name=node.name,
            args=tuple(checker.check_type(self, arg.annotation) if arg.annotation else NoType for arg in node.args.args),
            returns=checker.check_type(self, node.returns) if node.returns else NoType,
        )
        return NoValue

    def visit_ClassDef(self, node: ast.ClassDef) -> NoValue:
        class_def = Type(
            name=node.name,
            bases=tuple(checker.check_type(self, base) for base in node.bases),
            methods={},
        )

        self.namespace[node.name] = class_def
        return NoValue
