## Types

- Les types comme des fonctions
- Définition de classes
- Appel de méthodes
- Définition de méthodes
- Opérateurs (6d3c775)

## Appeler les types

```python
def check_call(visitor, func, args):
    if any(arg is NoValue for arg in args):
        return NoValue

    if isinstance(func, Callable) and func.match_args(*args):
        return func.apply(*args)

    if isinstance(func, TypeForm):
        return Value(type=func)

    visitor.add_error(CallError, function=getattr(func, 'name', ''), args=args)
    return NoValue
```

## Appeler les types

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

```python
base_type = Type(name='type')
TypeForm.type = base_type

builtins = {
    'int': Type(name='int'),
    'float': Type(name='float'),
    'str': Type(name='str'),
}

function_type = Type(name='function')
Callable.type = function_type
```

## Définition de classe

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

```python
class Callable(...):
    [...]

    def bind(self, value):
        return Method(function=self, value=value)

@dataclasses.dataclass(frozen=True)
class Function(...):
    [...]

@dataclasses.dataclass(frozen=True)
class Method(...):
    [...]
# Avoid this by reopening subclasses automatically + reapply decorator
# + allow some blocks to be reexecuted after a class has been modified?
```

## Méthodes

```python
@dataclasses.dataclass(frozen=True)
class Type(...):
    [...]

    name: str
    bases: tuple = ()
    methods: dict = dataclasses.field(repr=False, default_factory=dict)
```

## Méthodes

```python
class TypingVisitor(...):
    [...]

    def visit_ClassDef(self, node):
        class_def = Type(
            name=node.name,
            bases=tuple(check_type(self, base) for base in node.bases),
        )

        self.namespace[node.name] = class_def
        class_context = self.context.new_child()
        class_namespace = class_context.last.namespace

        with new_layer(self, context=class_context):
            self.generic_visit(node)

        class_def.methods.update(
            (name, value)
            for name, value in class_namespace.items()
            if isinstance(value, Function)
        )

        return NoValue
```

## Méthodes

```python
def get_method(value, method_name):
    if not isinstance(value.type, Type):
        return NoValue
    function = value.type.methods.get(method_name, NoValue)
    if function is NoValue:
        return NoValue
    return function.bind(value)
```

## Méthodes

```python
def check_call(visitor, func, args):
    if any(arg is NoValue for arg in args):
        return NoValue

    if isinstance(func, Callable) and func.match_args(*args):
        return func.apply(*args)

    if isinstance(func, TypeForm):
        return Value(type=func)

    visitor.add_error(CallError, function=getattr(func, 'name', ''), args=args)
    return NoValue
```

## Méthodes

```python
class TypingVisitor(...):
    [...]

    def visit_Attribute(self, node: ast.Attribute) -> PyObject:
        obj = self.visit(node.value)
        if isinstance(obj, PyObject) and isinstance(obj.type, Type):
            method = get_method(obj, node.attr)
            if method is not NoValue:
                return method
        self.add_error(Error, message=f'Unknown attribute {node.attr} on object of type {obj.type.name}')
        return NoValue
```

## Méthodes

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
