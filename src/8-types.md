# Types et classes

## Appeler les types

- Un type peut être vu comme une _fonction_ renvoyant une valeur du type demandé

```python
def check_call(visitor, func, args, node):
    if any(arg is NoValue for arg in args):
        return NoValue

    if isinstance(func, Callable) and func.match_args(*args):
        return func.apply(*args)

    if isinstance(func, TypeForm):
        return Value(type=func)

    visitor.add_error('Call Error', f'cannot call {getattr(func, 'name', '')} with arg types {", ".join(arg.type.name for arg in args)}', node=node)
    return NoValue
```

## Appeler les types

- Le premier prototype fonctionne comme attendu

```python
%%writefile assets/type_functions.py
a: int = 3 + int('5') # OK
b: str = str(3) + '5' # OK

b = str(3) + int('5') # KO
```

```python
check_files('assets/type_functions.py')
```

## Définition de classe

- On étend alors le concept aux types personnalisés, avec la définition de classes
    - Une classe se définit par son nom et ses parents

```python
@dataclasses.dataclass(frozen=True)
class Type(...):
    [...]
    name: str
    bases: tuple[TypeForm, ...] = ()

    def __le__(self, rhs):
        if self.bases:
            return any(base <= rhs for base in self.bases)
        if isinstance(rhs, __class__):
            return self.name is rhs.name
        return NotImplemented

    def __ge__(self, rhs):
        if self.bases:
            return any(base >= rhs for base in self.bases)
        if isinstance(rhs, __class__):
            return self.name is rhs.name
        return NotImplemented
```

## Définition de classe

- La classe est alors enregistrée lorsqu'on rencontre sa définition

```python
class TypingVisitor(...):
    [...]

    def visit_ClassDef(self, node):
        class_def = Type(
            name=node.name,
            bases=tuple(check_type(self, base) for base in node.bases),
        )

        self.namespace[node.name] = class_def
        return NoValue
```

## Définition de classe

- Cela nous autorise à utiliser nos propres types dans les annotations

```python
%%writefile assets/classes.py
class A:
    pass

a: A = A() # OK
b: int = A() # KO

c: A = 0 # KO

class D(int):
    pass

d: int = D() # OK

e: A | int = A() # OK
f: A | int = 5 # OK
g: A | int = '' # KO
h: A | int = D() # OK

i: D | int = A() # KO
j: D | int = D() # OK
k: D | int = 5 # OK
l: D | int = '' # KO
```

```python
check_files('assets/classes.py')
```

## Méthodes

- Une classe peut aussi contenir des méthodes
   - Les méthodes sont simplement des fonctions liées à une instance
   - Elles reçoivent cette instance en premier argument

```python
@dataclasses.dataclass(frozen=True)
class Method(Callable):
    function: Callable
    value: PyObject

    @property
    def name(self):
        return self.function.name

    @property
    def args(self):
        self_arg, *args = self.function.args
        assert self_arg is self.value.type
        return tuple(args)

    @property
    def returns(self):
        return self.function.returns

    def apply(self, *values):
        return self.function.apply(self.value, *values)
```

## Méthodes

- On permet à tout _callable_ d'être associé à une instance pour former une méthode

```python
class Callable(...):
    [...]

    def bind(self, value):
        return Method(function=self, value=value)
```

## Définition de méthodes

- Les méthodes se rapportent à la classe (type) dans laquelle elles sont défininies

```python
@dataclasses.dataclass(frozen=True)
class Type(...):
    [...]

    name: str
    bases: tuple = ()
    methods: dict = dataclasses.field(repr=False, default_factory=dict)
```

## Définition de méthodes

- Et sont donc découvertes lors de la définition de la classe, dans un espace de noms dédié

```python
from collections import ChainMap

class TypingVisitor(...):
    [...]

    def visit_ClassDef(self, node):
        class_def = Type(
            name=node.name,
            bases=tuple(check_type(self, base) for base in node.bases),
        )

        self.namespace[node.name] = class_def
        current_ns, current_ann, class_ns = self.namespace, self.annotations, {}

        self.namespace, self.annotations = ChainMap(class_ns, current_ns), ChainMap({}, current_ann)
        self.generic_visit(node)
        self.namespace, self.annotations = current_ns, current_ann

        class_def.methods.update(
            (name, value)
            for name, value in class_ns.items()
            if isinstance(value, Function)
        )

        return NoValue
```

## Appel de méthodes

- Pour appeler une méthode, il faut d'abord associer la fonction à l'instance
    - Cela permet le passage automatique de l'instance au paramètre `self`

```python
def get_method(value, method_name):
    if not isinstance(value.type, Type):
        return NoValue
    function = value.type.methods.get(method_name, NoValue)
    if function is NoValue:
        return NoValue
    return function.bind(value)
```

## Appel de méthodes

- La méthode est accédée comme un attribut de l'instance

```python
class TypingVisitor(...):
    [...]

    def visit_Attribute(self, node: ast.Attribute) -> PyObject:
        obj = self.visit(node.value)
        if isinstance(obj, PyObject) and isinstance(obj.type, Type):
            method = get_method(obj, node.attr)
            if method is not NoValue:
                return method
        self.add_error('Error', f'Unknown attribute {node.attr} on object of type {obj.type.name}', node=node)
        return NoValue
```

## Appel de méthodes

- Tout le reste fonctionne comme attendu car les méthodes sont des _callables_

```python
%%writefile assets/methods.py
class A:
    def test(self: A) -> int:
        return 0

    def pouet(self: A, value: str) -> str:
        return value + '!'

a: A = A() # OK
b: int = a.test() # OK
c: str = a.test() # KO

d: str = a.pouet('test') # OK
e: int = a.pouet('test') # KO
a.pouet(5) # KO

a.tutu() # KO
```

```python
check_files('assets/methods.py')
```

## Opérateurs en tant que méthodes

- Les opérateurs en eux-mêmes peuvent être vus comme des méthodes
    - C'est le cas dans le modèle objet de Python

```python
[...]
builtins['int'].methods['__init__'] = Function(
    name='__init__',
    args=(builtins['int'], builtins['int'] | builtins['float'] | builtins['str']),
    returns=builtins['int'],
)
builtins['int'].methods['__add__'] = Function(
    name='__add__',
    args=(builtins['int'], builtins['int']),
    returns=builtins['int'],
)

builtins['float'].methods['__init__'] = Function(
    name='__init__',
    args=(builtins['float'], builtins['int'] | builtins['float'] | builtins['str']),
    returns=builtins['float'],
)
builtins['float'].methods['__add__'] = Function(
    name='__add__',
    args=(builtins['float'], builtins['float'] | builtins['int']),
    returns=builtins['float'],
)

builtins['str'].methods['__init__'] = Function(
    name='__init__',
    args=(builtins['str'], builtins['str'] | builtins['int'] | builtins['float']),
    returns=builtins['str'],
)
builtins['str'].methods['__add__'] = Function(
    name='__add__',
    args=(builtins['str'], builtins['str']),
    returns=builtins['str'],
)
```

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
