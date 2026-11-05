# Écrire un analyseur de types

## Analyse statique

- L'analyse statique permet d'avaluer toutes les branches du programme
    - analyse le code sans l'exécuter
    - ne connaît donc pas toutes les conditions / données

- Mypy est un analyseur statique

## Arbre syntaxique (AST)

- Accéder aux annotations sans exécuter le code
    - Module `ast` pour parser un fichier Python

---

```python
%%writefile samples/test_ast.py
def func(a: int) -> int:
    return a + 1

print(func(5))
```

```python
import ast
from pathlib import Path

content = Path('samples/test_ast.py').read_text()
tree = ast.parse(content)
print(ast.dump(tree))
```

## Arbre syntaxique (AST)

- Visiteur (_visitor pattern_) pour parcourir les nœuds

```python
class PrintVisitor(ast.NodeVisitor):
    def visit(self, node):
        print(type(node))
        return super().visit(node)

PrintVisitor().visit(tree)
```

## Arbre syntaxique (AST)

- Peut être spécialisé par type de nœud

```python
class PrintVisitor(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        print('Defining', node.name)
        return self.generic_visit(node) # parcours récursif

    def visit_Call(self, node):
        print('Calling', node.func.id)
        return self.generic_visit(node)

PrintVisitor().visit(tree)
```

- Tous les types de nœuds documentés sur [docs.python.org/fr/3/library/ast.html](https://docs.python.org/fr/3/library/ast.html)

## Analyseur de types

- Construction d'un visiteur pour contrôler les types
    - Commencer par analyser les assignations
    - Nœuds `AnnAssign`, `Name` et `Constant`

---

- `Constant` : la valeur Python littérale qui est assignée

```python
class TypingVisitor(ast.NodeVisitor):
    def visit_Constant(self, node) -> object:
        return node.value
```

## Analyseur de types

- `Name` : le nom du type utilisé comme annotation
- Première ébauche de gestion d'erreur

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

## Analyseur de types

- `AnnAssign` : l'assignation annotée en tant que telle

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

## Analyseur de types

- Exécution sur un fichier de test

```python
%%writefile assets/assignment.py
a: int = 0 # OK
b: int = "5" # KO
b: str = "" # OK
c: str = 0 # KO
```

```python
visitor = TypingVisitor()
visitor.visit(ast.parse(Path('assets/assignment.py').read_text()))
```

## Contexte d'analyse

- Gestion du contexte : nom de fichier et numéro de ligne
- Meilleur traitement des erreurs : stockage plutôt qu'affichage

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

## Point d'entrée

- Construction d'une classe `Typy` pour aider au traitement des fichiers
- Point d'entrée de notre analyseur statique de types

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
```

## Point d'entrée

- Chargée de collecter et afficher les erreurs

```python
class Typy:
    [...]

    @property
    def errors(self) -> list[str]:
        return self.visitor.errors

    def print_errors(self) -> None:
        for error in self.errors:
            print(error)
```

## Premier analyseur

- Fonction utilitaire pour lancer `Typy`

```python
def check_files(*paths):
    typy = Typy()
    typy.run_path(*paths)
    typy.print_errors()
```

```sh
%load assets/assignment.py
```

```python
check_files('assets/assignment.py')
```
