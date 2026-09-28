## Espaces de noms

- Gestion du namespace

## Espaces de noms

```python
class TypingVisitor(...):
    [...]

    def __init__(self):
        self.filename = None
        self.annotations = {}
        self.namespace = {}
        self.errors = []

    def visit_file(self, node, filename):
        self.filename = filename
        self.annotations.clear()
        self.namespace.clear()
        return self.visit(node)

    def visit_Name(self, node: ast.Name) -> PyObject:
        if node.id in self.namespace:
            return self.namespace[node.id]
        if node.id in builtins:
            return builtins[node.id]
        self.add_error('Error', f'{node.id} variable not found')
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
    visitor.namespace[varname] = value

    if not annotation.match(value):
        visitor.add_error('Assignment error', f'Trying to assign value of type {value.type.name} to variable {varname} annotated with {annotation.name}', node=target_node)
```

## Espaces de noms

```python
check_files('assets/assignment.py')
```
