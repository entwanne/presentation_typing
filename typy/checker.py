import ast
import typing

from .object import Type, NoValue

if typing.TYPE_CHECKING:
    from .visitor import TypingVisitor


def check_type(visitor: TypingVisitor, node: ast.AST) -> Type:
    'Helper function to ensure that a node contains a type'
    type = visitor.visit(node)
    if isinstance(type, Type):
        return type
    visitor.add_error('Error', f'{type!r} is not a type', node=node)
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
        visitor.add_error('Error', f'{varname} variable already defined', node=target_node)
        return
    else:
        try:
            annotation = check_type(visitor, annotation_node)
            if annotation is NoValue:
                return
        except ValueError as e:
            visitor.add_error('Error', str(e), node=target_node)
            return
        annotations[varname] = annotation

    if value is NoValue:
        return

    if not annotation.match(value):
        visitor.add_error('Assignment error', f'Trying to assign value of type {value.type.name} to variable {varname} annotated with {annotation.name}', node=target_node)
