# Fonctions et opérations

## Fonctions et opérations

- Gestion du namespace
- Définitions de fonctions et appels
- Opérateurs binaires

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

```sh
%load assets/assignment.py
```

```python
check_files('assets/assignment.py')
```

## Définition de fonction

```python
class Callable(PyObject):
    name: str
    args: tuple[TypeForm, ...]
    returns: TypeForm
    type: typing.ClassVar[Type]

    def match_args(self, *values):
        return len(self.args) == len(values) and all(arg_type.match(value) for arg_type, value in zip(self.args, values))

    def apply(self, *args: PyObject) -> PyObject:
        return Value(type=self.returns)
```

```python
@dataclasses.dataclass(frozen=True)
class Function(Callable):
    name: str
    args: tuple[TypeForm, ...]
    returns: TypeForm
```

## Définition de fonction

```python
[...]
function_type = Type(name='function')
Callable.type = function_type
```

## Définition de fonction

```python
class TypingVisitor(...):
    [...]

    def visit_FunctionDef(self, node: ast.FunctionDef) -> NoValue:
        self.namespace[node.name] = Function(
            name=node.name,
            args=tuple(check_type(self, arg.annotation) if arg.annotation else NoType for arg in node.args.args),
            returns=check_type(self, node.returns) if node.returns else NoType,
        )
        return NoValue
```

## Appel de fonction

```python
def check_call(visitor, func, args, node):
    if any(arg is NoValue for arg in args):
        return NoValue

    if isinstance(func, Callable) and func.match_args(*args):
        return func.apply(*args)

    visitor.add_error('Call Error', f'cannot call {func.name} with arg types {", ".join(arg.type.name for arg in args)}', node=node)
    return NoValue
```

## Appel de fonction

```python
class TypingVisitor(...):
    [...]

    def visit_Call(self, node: ast.Call) -> PyObject:
        func = self.visit(node.func)
        args = tuple(self.visit(arg) for arg in node.args)
        return check_call(self, func, args, node)
```

## Appel de fonction

```python
%%writefile assets/functions.py
def func() -> int:
    return 0

a: int = func() # OK
b: str = func() # KO

def addition(a: int, b: int) -> int:
    return a + b

addition(3, 5) # OK
addition(3, '5') # KO
addition('3', '5') # KO
```

```python
check_files('assets/functions.py')
```

## Opérateurs binaires

```python
def check_operation(visitor, operator, left, right, node):
    if left is NoValue or right is NoValue:
        return NoValue

    if operator is ast.BitOr and isinstance(left, TypeForm) and isinstance(right, TypeForm):
        return left | right

    if operator is ast.Add and left.type is builtins['int'] and right.type is builtins['int']:
        return Value(type=builtins['int'])

    if operator is ast.Add and left.type is builtins['str'] and right.type is builtins['str']:
        return Value(type=builtins['str'])

    if operator is ast.Add and left.type is builtins['float'] and right.type in (builtins['float'], builtins['int']):
        return Value(type=builtins['float'])

    visitor.add_error('Expression error', f'Incompatible operation {operator.__name__} for values of types {left.type.name} and {right.type.name}', node=node)
    return NoValue
```

## Opérateurs binaires

```python
class TypingVisitor(...):
    [...]

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return check_operation(self, type(node.op), left, right, node)
```

## Opérateurs binaires

```python
%%writefile assets/operations.py
a: int = 3 + 5 # OK
a = 1 + 2 + 3 + 4 # OK
a = 3 + '5' # KO

b: str = 'a' + 'b' # OK
b = 3 + 2 # KO
```

```python
check_files('assets/operations.py')
```
