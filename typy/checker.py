import ast
import typing

from . import error
from .object import PyObject, Type, TypeForm, Method, NoValue

if typing.TYPE_CHECKING:
    from .visitor import TypingVisitor


# + override typing module in import mechanism to point to a custom one? (defining Any and other stuff)

operators = {
    ast.BitOr: '__or__',
    ast.Add: '__add__',
    ast.Call: '__call__',
}


def get_method(value: PyObject, method_name: str) -> Method:
    'Helper function to get the method of an object'
    if not isinstance(value.type, Type):
        return NoValue
    function = value.type.methods.get(method_name, NoValue)
    if function is NoValue:
        return NoValue
    return function.bind(value)


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


def check_operation(visitor: TypingVisitor, operator: type[ast.operator | ast.Call], args: tuple[PyObject, ...], error_args: dict[str, typing.Any]) -> PyObject:
    'Helper function to check that an operation is valid'
    if not args or any(arg is NoValue for arg in args):
        return NoValue

    method_name = operators.get(operator)
    if method_name is None:
        visitor.add_error(**error_args)
        return NoValue

    value, args = args[0], args[1:]
    method = get_method(value, method_name)
    if method is NoValue:
        visitor.add_error(**error_args)
        return NoValue

    if method.match_args(*args):
        return method.apply(*args)

    visitor.add_error(**error_args)
    return NoValue
