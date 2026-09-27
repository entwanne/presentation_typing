## Fonctions et opérations

- Définitions de fonctions et appels
- Opérateurs binaires

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
def check_call(visitor, func, args):
    if any(arg is NoValue for arg in args):
        return NoValue

    if isinstance(func, Callable) and func.match_args(*args):
        return func.apply(*args)

    visitor.add_error(CallError, function=getattr(func, 'name', ''), args=args)
    return NoValue
```

## Appel de fonction

```python
@dataclasses.dataclass(frozen=True)
class CallError(BaseError):
    function: str
    args: tuple

    title: typing.ClassVar[str] = 'Call error'

    @property
    def message(self) -> str:
        return f'cannot call {self.function} with arg types {", ".join(arg.type.name for arg in self.args)}'
```

## Appel de fonction

```python
class TypingVisitor(...):
    [...]

    def visit_Call(self, node: ast.Call) -> PyObject:
        func = self.visit(node.func)
        args = tuple(self.visit(arg) for arg in node.args)
        return check_call(self, func, args)
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
def check_operation(visitor, operator, left, right):
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

    visitor.add_error(ExpressionError, operation=operator.__name__, values=(left, right))
    return NoValue
```

## Opérateurs binaires

```python
class TypingVisitor(...):
    [...]

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return check_operation(self, type(node.op), left, right)
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
