## Espaces de noms

- Gestion du curseur et du contexte
- Gestion du namespace

## Curseur

```python
@dataclasses.dataclass(frozen=True)
class Cursor:
    filename: str | None = None
    line: int | None = None
    col: int | None = None

    def replace(self, **kwargs: typing.Any) -> typing.Self:
        return dataclasses.replace(
            self,
            **{
                key: value
                for key, value in kwargs.items()
                if value is not None
            },
        )

    def __str__(self) -> str:
        if self.filename is not None:
            if self.line is not None:
                return f'{self.filename}::{self.line}'
            return self.filename
        return ''
```

## Erreurs

```python
@dataclasses.dataclass(frozen=True)
class BaseError:
    cursor: Cursor

    title: typing.ClassVar[str] = 'Error'

    @property
    def location(self) -> str:
        return str(self.cursor)

    def __str__(self) -> str:
        message = getattr(self, 'message', '')
        if location := self.location:
            return f'{self.title} on {location}: {message}'
        return f'{self.title}: {message}'
```

## Erreurs

```python
@dataclasses.dataclass(frozen=True)
class Error(BaseError):
    message: str
```

## Erreurs

```python
@dataclasses.dataclass(frozen=True)
class AssignmentError(BaseError):
    dest: str
    annotation: TypeForm
    type: TypeForm

    title: typing.ClassVar[str] = 'Assignment error'

    @property
    def message(self) -> str:
        return f'Trying to assign value of type {self.type.name} to variable {self.dest} annotated with {self.annotation.name}'
```

## Erreurs

```python
@dataclasses.dataclass(frozen=True)
class ExpressionError(BaseError):
    operation: str
    values: tuple

    title: typing.ClassVar[str] = 'Expression error'

    @property
    def message(self) -> str:
        types = tuple(value.type.name if value else 'None' for value in self.values)
        match types:
            case ():
                return f'Incompatible operation {self.operation}'
            case (t,):
                return f'Incompatible operation {self.operation} for value of type {t}'
            case (*left, right):
                return f'Incompatible operation {self.operation} for values of types {", ".join(left)} and {right}'
        return ''
```

## Erreurs

```python
class TypingVisitor(...):
    [...]

    def __init__(self):
        self.annotations = {}
        self.cursor = Cursor()
        self.errors = []

    def add_error(self, error_type, **kwargs):
        self.errors.append(error_type(**kwargs, cursor=self.cursor))

    def visit_file(self, node, filename):
        self.annotations.clear()
        self.cursor = self.cursor.replace(filename=filename)
        return self.visit(node)
```

## Erreurs

```python
def check_type(visitor, node):
    type = visitor.visit(node)
    if isinstance(type, TypeForm):
        return type
    visitor.add_error(Error, message=f'{type!r} is not a type')
    return NoValue
```

## Erreurs

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
        visitor.add_error(Error, message=f'{varname} variable already defined')
        return
    else:
        try:
            annotation = check_type(visitor, annotation_node)
            if annotation is NoValue:
                return
        except ValueError as e:
            visitor.add_error(Error, message=str(e))
            return
        annotations[varname] = annotation

    if value is NoValue:
        return

    if not annotation.match(value):
        visitor.add_error(AssignmentError, dest=varname, annotation=annotation, type=value.type)
```

## Erreurs

```python
check_files('assets/assignment.py')
```

## Contexte

```python
class TypingVisitor(...):
    [...]

    def visit(self, node):
        assert node is not None

        self.cursor = self.cursor.replace(
            line=getattr(node, 'lineno', None),
            col=getattr(node, 'col_offset', None),
        )
        value = super().visit(node)
        if not isinstance(value, PyObject):
            raise ValueError(f'Visit call returned a value of type {type(value).__qualname__} for node {type(node).__qualname__} which is not a PyObject')
        return value
```

## Contexte

```python
check_files('assets/assignment.py')
```

## Espaces de noms

```python
class TypingVisitor(...):
    [...]

    def __init__(self):
        self.annotations = {}
        self.namespace = {}
        self.cursor = Cursor()
        self.errors = []

    def visit_file(self, node, filename):
        self.cursor = self.cursor.replace(filename=filename)
        self.annotations.clear()
        self.namespace.clear()
        return self.visit(node)

    def visit_Name(self, node: ast.Name) -> PyObject:
        if node.id in self.namespace:
            return self.namespace[node.id]
        if node.id in builtins:
            return builtins[node.id]
        self.add_error(Error, message=f'{node.id} variable not found')
        return NoValue
```

## Espaces de noms

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
        visitor.add_error(Error, message=f'{varname} variable already defined')
        return
    else:
        try:
            annotation = check_type(visitor, annotation_node)
            if annotation is NoValue:
                return
        except ValueError as e:
            visitor.add_error(Error, message=str(e))
            return
        annotations[varname] = annotation

    if value is NoValue:
        return
    visitor.namespace[varname] = value

    if not annotation.match(value):
        visitor.add_error(AssignmentError, dest=varname, annotation=annotation, type=value.type)
```

## Espaces de noms

```python
check_files('assets/assignment.py')
```
