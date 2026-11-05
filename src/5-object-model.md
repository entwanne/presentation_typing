# Modèle objet de Python

## Modèle objet de Python

- Répliquer le modèle objet de Python pour mieux l'analyser

---

- Une valeur est l'instance d'un type

<div align="center"><img src="img/type_model_schema_1.png" /></div>

## Modèle objet de Python

- Une valeur est l'instance d'un type

```python
import dataclasses

@dataclasses.dataclass(frozen=True)
class Value:
    type: type

class TypingVisitor(...):
    [...]

    def visit_Constant(self, node) -> Value:
        return Value(type=type(node.value))

    def visit_AnnAssign(self, node):
        if node.value is None:
            return

        value = self.visit(node.value)
        if not isinstance(value, Value):
            return

        annotation = self.visit(node.annotation)
        if not isinstance(annotation, type):
            self.add_error('Error', f'{annotation!r} is not a type', node=annotation_node)
            return

        if value.type is not annotation:
            self.add_error('Assignment error', f'Trying to assign value of type {value.type.__name__} to variable {node.target.id} annotated with {annotation.__name__}', node=node.target)
```

## Modèle objet de Python

- Chaque type hérite d'`object`

<div align="center"><img src="img/type_model_schema_2.png" /></div>

## Modèle objet de Python

- Et chaque type est une instance de `type`

<div align="center"><img src="img/type_model_schema_3.png" /></div>

## Modèle objet de Python

- Et chaque type est une instance de `type`

```python
import typing

class PyObject:
    type: Type

@dataclasses.dataclass(frozen=True)
class Type(PyObject):
    name: str
    type: typing.ClassVar[Type]

    def match(self, value: PyObject) -> bool:
        return value.type is self

    def __str__(self) -> str:
        return f'<Type:{self.name}>'

@dataclasses.dataclass(frozen=True)
class Value(PyObject):
    type: Type
```

## Modèle cyclique

- `type` est lui-même une instance de `type`

<div align="center"><img src="img/type_model_schema_4.png" /></div>

## Modèle cyclique

- `type` est lui-même une instance de `type`

```python
[...]
base_type = Type(name='type')
Type.type = base_type
```

## Adaptations au modèle

- Recréons les _builtins_ pour correspondre à notre nouveau modèle

```python
[...]
builtins = {
    'int': Type(name='int'),
    'float': Type(name='float'),
    'str': Type(name='str'),
}
```

---

- Et de quoi représenter l'absence de valeur

```python
[...]
NoType = Type('NoType')
NoValue = Value(type=NoType)
```

## Adaptations au modèle

- Prise en compte du modèle et des _builtins_ dans l'analyseur
- Ainsi que des instructions qui n'ont pas de valeur

```python
class TypingVisitor(...):
    [...]

    def visit(self, node):
        assert node is not None
        value = super().visit(node)
        if not isinstance(value, PyObject):
            raise ValueError(f'Visit call returned a value of type {type(value).__qualname__} for node {type(node).__qualname__} which is not a PyObject')
        return value

    def generic_visit(self, node):
        super().generic_visit(node)
        return NoValue

    def visit_Constant(self, node):
        return Value(type=builtins[type(node.value).__name__])
```

## Adaptations au modèle

- Idem dans la gestion des annotations

```python
class TypingVisitor(...):
    [...]

    def visit_Name(self, node: ast.Name) -> PyObject:
        if node.id in builtins:
            return builtins[node.id]
        self.add_error('Error', f'{node.id} type not found', node=node)
        return NoType

    def visit_AnnAssign(self, node: ast.AnnAssign) -> NoValue:
        if node.value is None:
            return

        value = self.visit(node.value)
        if value is NoValue:
            return NoValue

        annotation = self.visit(node.annotation)
        if not isinstance(annotation, Type):
            self.add_error('Error', f'{annotation!r} is not a type', node=node.annotation)
            return NoValue

        if not annotation.match(value):
            self.add_error('Assignment error', f'Trying to assign value of type {value.type.name} to variable {node.target.id} annotated with {annotation.name}', node=node.target)

        return NoValue
```

## Exécution de l'analyseur

- Pas de changement à l'exécution
    - Mais un modèle plus solide pour la suite

```sh
%load assets/assignment.py
```

```python
check_files('assets/assignment.py')
```
