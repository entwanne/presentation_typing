import ast
import builtins


class TypingVisitor(ast.NodeVisitor):
    'AST visitor to check types for assignments & operations'

    def __init__(self):
        self.filename = None

    def print_error(self, title, error, node=None) -> None:
        parts = [title]
        if self.filename:
            parts.append(f' on {self.filename}')
            if node:
                parts.append(f'::{node.lineno}')
        parts.append(f': {error}')
        print(''.join(parts))

    # Entrypoints

    def visit_file(self, node, filename):
        self.filename = filename
        return self.visit(node)

    # Node visit methods

    def visit_Constant(self, node) -> object:
        return node.value

    def visit_Name(self, node) -> type | None:
        if hasattr(builtins, node.id):
            return getattr(builtins, node.id)
        self.print_error('Error', f'{node.id} type not found', node=node)

    def visit_AnnAssign(self, node):
        if node.value is None:
            return

        value = self.visit(node.value)

        annotation = self.visit(node.annotation)
        if not isinstance(annotation, type):
            self.print_error('Error', f'{annotation!r} is not a type', node=node.annotation)
            return

        if not isinstance(value, annotation):
            self.print_error('Assignment error', f'Trying to assign value of type {type(value).__name__} to variable {node.target.id} annotated with {annotation.__name__}', node=node.target)
