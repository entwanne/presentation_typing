import ast
from pathlib import Path

from .visitor import TypingVisitor


class Typy:
    'Type-checker class'

    def __init__(self):
        self.visitor = TypingVisitor()

    def run_tree(self, tree: ast.AST, filename: str) -> None:
        self.visitor.visit_file(tree, filename)

    def run_source(self, source: str, filename: str) -> None:
        self.run_tree(ast.parse(source, filename=filename), filename)

    def run_file(self, file, filename: str | None = None) -> None:
        self.run_source(file.read(), filename or file.name)

    def run_path(self, *paths: str | Path) -> None:
        for path in paths:
            with open(path) as file:
                self.run_file(file)


__all__ = ['Typy']
