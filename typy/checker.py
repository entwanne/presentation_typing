import ast
import typing

from . import builtins, error
from .object import PyObject, TypeForm, Callable, Value, NoValue

if typing.TYPE_CHECKING:
    from .visitor import TypingVisitor


def check_type(visitor: TypingVisitor, node: ast.AST) -> TypeForm:
    'Helper function to ensure that a node contains a type'
    type = visitor.visit(node)
    if isinstance(type, TypeForm):
        return type
    visitor.add_error(error.Error, message=f'{type!r} is not a type')
    return NoValue


def check_assign(visitor: TypingVisitor, target_node: ast.AST, value_node: ast.AST | None, annotation_node: ast.AST | None = None) -> None:
    'Helper function to check that an assignment is valid'
    assert isinstance(target_node, ast.Name)
    varname = target_node.id
    annotations = visitor.annotations

    value = visitor.visit(value_node) if value_node is not None else NoValue

    if annotation_node is None:
        if varname in annotations:
            annotation = annotations[varname]
        else:
            return
    elif varname in annotations:
        visitor.add_error(error.Error, message=f'{varname} variable already defined')
        return
    else:
        try:
            annotation = check_type(visitor, annotation_node)
            if annotation is NoValue:
                return
        except ValueError as e:
            visitor.add_error(error.Error, message=str(e))
            return
        annotations[varname] = annotation

    if value is NoValue:
        return
    visitor.namespace[varname] = value

    if not annotation.match(value):
        visitor.add_error(error.AssignmentError, dest=varname, annotation=annotation, type=value.type)


def check_operation(visitor: TypingVisitor, operator: type[ast.operator], left: PyObject, right: PyObject) -> PyObject:
    'Helper function to check that an operation is valid'
    if left is NoValue or right is NoValue:
        return NoValue

    if operator is ast.BitOr and isinstance(left, TypeForm) and isinstance(right, TypeForm):
        return left | right

    if operator is ast.Add and left.type is builtins.int and right.type is builtins.int:
        return Value(type=builtins.int)

    if operator is ast.Add and left.type is builtins.str and right.type is builtins.str:
        return Value(type=builtins.str)

    if operator is ast.Add and left.type is builtins.float and right.type in (builtins.float, builtins.int):
        return Value(type=builtins.float)

    visitor.add_error(error.ExpressionError, operation=operator.__name__, values=(left, right))
    return NoValue


def check_call(visitor: TypingVisitor, func: PyObject, args: tuple[PyObject, ...]) -> PyObject:
    'Helper function to check that an operation is valid'
    if any(arg is NoValue for arg in args):
        return NoValue

    if isinstance(func, Callable) and func.match_args(*args):
        return func.apply(*args)

    visitor.add_error(error.CallError, function=getattr(func, 'name', ''), args=args)
    return NoValue
