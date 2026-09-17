import ast
import builtins
import sys


class TypingVisitor(ast.NodeVisitor):
    'AST visitor to check types for assignments & operations'

    def print_error(self, title, error, node) -> None:
        print(f'{title} on line {node.lineno}: {error}')

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
            self.print_error('Error', f'{annotation!r} is not a type', node=annotation_node)
            return

        if not isinstance(value, annotation):
            self.print_error('Assignment error', f'Trying to assign value of type {type(value).__name__} to variable {node.target.id} annotated with {annotation.__name__}', node=node.target)


if __name__ == '__main__':
    visitor = TypingVisitor()
    with open(sys.argv[1]) as f:
        visitor.visit(ast.parse(f.read()))
