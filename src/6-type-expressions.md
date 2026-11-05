# Expressions de types

## Nettoyage du code

- Nettoyage du visiteur : sortir ce qui peut l'être
    - comme la vérification de type

```python
def check_type(visitor, node):
    type = visitor.visit(node)
    if isinstance(type, Type):
        return type
    visitor.add_error('Error', f'{type!r} is not a type', node=node)
    return NoValue
```

## Assignations multiples

- Ou la vérification des annotations
- On en profite pour implémenter la réassignation

```python
def check_assign(visitor, target_node, value_node, annotation_node=None):
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
```

## Assignations multiples

- Implémentation au niveau du visiteur
    - via la méthode `visit_Assign` complémentaire à `visit_AnnAssign`

```python
class TypingVisitor(...):
    [...]

    def __init__(self):
        self.filename = None
        self.annotations = {}
        self.errors = []

    def visit_file(self, node, filename):
        self.filename = filename
        self.annotations.clear()
        return self.visit(node)

    def visit_Assign(self, node: ast.Assign) -> NoValue:
        for target in node.targets:
            check_assign(self, target, node.value)
        return NoValue

    def visit_AnnAssign(self, node: ast.AnnAssign) -> NoValue:
        check_assign(self, node.target, node.value, node.annotation)
        return NoValue
```

## Assignations multiples

- Elles sont bien prises en compte par l'analyseur

```python
%%writefile assets/assignment.py
a: int = 0 # OK
a = 5 # OK
a = "5" # KO

b: str
b = "" # OK
b = 0 # KO

b: str = "" # KO

c: int = 12 # OK

d: str = 12 # KO
```

```python
check_files('assets/assignment.py')
```

## Expressions de types

- Une variable peut-être annotée avec bien plus qu'un simple type
    - Repenser le type comme un ensemble de valeurs autorisées

```python
class PyObject:
    type: TypeForm

class TypeForm(PyObject):
    name: str
    type: typing.ClassVar[Type]

    def match(self, value: PyObject) -> bool:
        return value.type <= self

    def __le__(self, type: TypeForm) -> bool:
        return NotImplemented

    def __str__(self) -> str:
        return f'<Type:{self.name}>'
```

```python
[...]
TypeForm.type = base_type
```

## Expressions de types

- Et le type « concret » comme un cas particulier

```python
@dataclasses.dataclass(frozen=True)
class Value(PyObject):
    type: TypeForm

@dataclasses.dataclass(frozen=True)
class Type(TypeForm):
    name: str

    def __le__(self, rhs: TypeForm) -> bool:
        if isinstance(rhs, __class__):
            return self.name is rhs.name
        return NotImplemented

    def __ge__(self, rhs: TypeForm) -> bool:
        if isinstance(rhs, __class__):
            return self.name is rhs.name
        return NotImplemented
```

## Expressions de types

- Ce qui nous amène à redéfinir l'absence de valeur / type

```python
import functools

class _NoType(TypeForm):
    @functools.cache
    def __new__(cls):
        return super().__new__(cls)

    @property
    def name(self):
        return '<NoType>'

    def __le__(self, rhs):
        return False

    def __ge__(self, lhs):
        return False

class _NoValue(PyObject):
    @functools.cache
    def __new__(cls):
        return super().__new__(cls)

    @property
    def type(self):
        return NoType

    def __repr__(self):
        return '<NoValue>'
```

```python
[...]
NoType = _NoType()
NoValue = _NoValue()
```

## Expressions de types

- Et prendre en compte ces expressions de type dans notre vérification

```python
def check_type(visitor, node):
    type = visitor.visit(node)
    if isinstance(type, TypeForm):
        return type
    visitor.add_error('Error', f'{type!r} is not a type', node=node)
    return NoValue
```

## Expressions de types

- Toujours pas de changement visible sur l'analyse

```sh
%load assets/assignment.py
```

```python
check_files('assets/assignment.py')
```

## Union de types

- Mais permet l'introduction de l'union de types

```python
@dataclasses.dataclass(frozen=True)
class UnionType(TypeForm):
    types: tuple[TypeForm, ...]

    @classmethod
    def from_types(cls, *types):
        return cls(types)

    @property
    def name(self):
        return f'({" | ".join(t.name for t in self.types)})'

    def __le__(self, type):
        return any(subtype <= type for subtype in self.types)

    def __ge__(self, type):
        return any(subtype >= type for subtype in self.types)
```

## Union de types

- À intégrer directement via l'opérateur d'union (`|`)

```python
class TypeForm(...):
    [...]

    def __or__(self, rhs):
        return UnionType.from_types(self, rhs)

@dataclasses.dataclass(frozen=True)
class UnionType(...):
    [...]

    def __or__(self, rhs):
        if isinstance(rhs, __class__):
            return __class__.from_types(*self.types, *rhs.types)
        else:
            return __class__.from_types(*self.types, rhs)

    def __ror__(self, lhs):
        # lhs n'est pas un UnionType, sinon on serait passé par __or__
        return __class__.from_types(lhs, *self.types)
```

## Union de types

- Qui nécessite de traiter l'opération dans le visiteur

```python
class TypingVisitor(...):
    [...]

    def visit_BinOp(self, node) -> TypeForm:
        left = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(node.op, ast.BitOr) and isinstance(left, TypeForm) and isinstance(right, TypeForm):
            return left | right

        return NoType
```

## Union de types

- Et offre plus de possibilités lors du typage

```python
%%writefile assets/assignment.py
a: int = 0 # OK
a = 5 # OK
a = "5" # KO

b: str
b = "" # OK
b = 0 # KO

b: str = "" # KO

c: int = 12 # OK

d: str = 12 # KO

e: int | float = 0 # OK
e = 0.5 # OK
f: int | float = 0.1 # OK
g: int | float = '' # KO
```

```python
check_files('assets/assignment.py')
```
