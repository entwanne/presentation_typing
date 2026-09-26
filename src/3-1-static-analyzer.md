# Écrire un analyseur de types

## Analyse statique

- Module `ast`, `ast.parse` et `NodeVisitor`
    - méthodes `visit_XXX`

## Analyse statique

```python
import ast

class TypingVisitor(ast.NodeVisitor):
    def visit_Constant(self, node) -> object:
        return node.value
```

## Analyse statique

```python
import builtins

class TypingVisitor(...):
    [...]

    def add_error(self, title, error, node) -> None:
        print(f'{title} on line {node.lineno}: {error}')

    def visit_Name(self, node) -> type | None:
        if hasattr(builtins, node.id):
            return getattr(builtins, node.id)
        self.add_error('Error', f'{node.id} type not found', node=node)
```

## Analyse statique

```python
class TypingVisitor(...):
    [...]

    def visit_AnnAssign(self, node):
        if node.value is None:
            return

        value = self.visit(node.value)

        annotation = self.visit(node.annotation)
        if not isinstance(annotation, type):
            self.add_error('Error', f'{annotation!r} is not a type', node=annotation_node)
            return

        if not isinstance(value, annotation):
            self.add_error('Assignment error', f'Trying to assign value of type {type(value).__name__} to variable {node.target.id} annotated with {annotation.__name__}', node=node.target)
```

## Analyse statique

```python
%%writefile assets/assignment.py
a: int = 0 # OK
b: int = "5" # KO
b: str = "" # OK
c: str = 0 # KO
```

```python
from pathlib import Path
visitor = TypingVisitor()
visitor.visit(ast.parse(Path('assets/assignment.py').read_text()))
```

## Analyse statique

```python
class TypingVisitor(...):
    [...]

    def __init__(self):
        self.filename = None
        self.errors = []

    def visit_file(self, node, filename):
        self.filename = filename
        return self.visit(node)

    def add_error(self, title, error, node=None) -> None:
        parts = [title]
        if self.filename:
            parts.append(f' on {self.filename}')
            if node:
                parts.append(f'::{node.lineno}')
        parts.append(f': {error}')
        self.errors.append(''.join(parts))
```

## Analyse statique

```python
class Typy:
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

    @property
    def errors(self) -> list[str]:
        return self.visitor.errors

    def print_errors(self) -> None:
        for error in self.errors:
            print(error)
```

## Analyse statique

```python
typy = Typy()
typy.run_path('assets/assignment.py')
typy.print_errors()
```
