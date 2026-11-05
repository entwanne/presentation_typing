# Un peu de magie


## Opérateurs plus complexes

- Attention, on entre maintenant dans les parties obscures de cette présentation
- On a besoin de quelques ajustements pour les opérateurs d'union (`__or__`) et d'appel (`__call__`)
    - Qui nécessitent d'exécuter du code pour déterminer leurs caractéristiques

---

- Une première fonction dont le type de retour (l'application) est défini à la volée

```python
import collections.abc

@dataclasses.dataclass(frozen=True)
class ApplicationFunction(Function):
    apply: collections.abc.Callable
```

## Opérateurs plus complexes

- Et une seconde pour faire dépendre toutes les caractéristiques d'une classe

```python
@dataclasses.dataclass(frozen=True)
class DynamicFunction(Callable):
    dynamic: collections.abc.Callable[[PyObject | None], Callable]

    @property
    def name(self):
        return self.dynamic(None).name

    @property
    def args(self) -> tuple[TypeForm, ...]:
        return self.dynamic(None).args

    @property
    def returns(self) -> TypeForm:
        return self.dynamic(None).returns

    def apply(self, *args: PyObject) -> PyObject:
        return self.dynamic(None).apply(*args)

    def bind(self, value: PyObject) -> DynamicMethod:
        return DynamicMethod(function=self, value=value)
```

## Opérateurs plus complexes

- Avec son type de méthode associé

```python
class DynamicMethod(Method):
    function: DynamicFunction

    @property
    def args(self) -> tuple[TypeForm, ...]:
        return self.function.dynamic(self.value).args

    @property
    def returns(self) -> TypeForm:
        return self.function.dynamic(self.value).returns
```

## Opérateurs plus complexes

- On redéfinit alors l'union entre types et l'instanciation (appel) de type

```python
[...]
base_type.methods['__or__'] = DynamicFunction(
    lambda cls: ApplicationFunction(
        name='__or__',
        args=(base_type, base_type) if cls is None else (base_type,),
        returns=base_type,
        apply=lambda cls, rhs: UnionType(types=(cls, rhs)),
    ),
)
base_type.methods['__call__'] = DynamicFunction(
    lambda cls: ApplicationFunction(
        name='__call__',
        args=() if cls is None else cls.methods['__init__'].args[1:] if '__init__' in cls.methods else (),
        returns=cls,
        apply=lambda cls, *args: Value(type=cls),
    ),
)
```

## Opérateurs plus complexes

- Idem pour l'appel de fonction

```python
[...]
function_type.methods['__call__'] = DynamicFunction(
    lambda func: ApplicationFunction(
        name='__call__',
        args=() if func is None else func.args,
        returns=None if func is None else func.returns,
    ),
)
```

## Opérateurs en tant que méthodes

- On associe les noms de méthodes aux opérateurs

```python
operators = {
    ast.BitOr: '__or__',
    ast.Add: '__add__',
    ast.Call: '__call__',
}
```

## Opérateurs en tant que méthodes

- On transforme la vérification des opérations pour faire appel aux méthodes associées

```python
def check_operation(visitor, operator, args, error_args):
    if not args or any(arg is NoValue for arg in args):
        return NoValue

    method_name = operators.get(operator)
    if method_name is None:
        visitor.add_error(*error_args)
        return NoValue

    value, args = args[0], args[1:]
    method = get_method(value, method_name)
    if method is NoValue:
        visitor.add_error(*error_args)
        return NoValue

    if method.match_args(*args):
        return method.apply(*args)

    visitor.add_error(*error_args)
    return NoValue
```

## Opérateurs en tant que méthodes

- Et l'on branche tout ça dans le visiteur

```python
class TypingVisitor(...):
    [...]

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return check_operation(
            self,
            type(node.op),
            (left, right),
            error_args=(
                'Expression Error',
                f'Incompatible operation {type(node.op).__name__} for values of types {left.type.name} and {right.type.name}',
                node,
            ),
        )

    def visit_Call(self, node):
        func = self.visit(node.func)
        args = tuple(self.visit(arg) for arg in node.args)
        return check_operation(
            self,
            ast.Call,
            (func, *args),
            error_args=(
                'Call Error',
                f'cannot call {getattr(func, 'name', '')} with arg types {", ".join(arg.type.name for arg in args)}',
                node,
            ),
        )
```

## Opérateurs en tant que méthodes

- Toujours compatible avec notre fichier d'exemple

```sh
%load assets/operations.py
```

```python
check_files('assets/operations.py')
```
