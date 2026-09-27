## Types

- Les types comme des fonctions
- Définition de classes
- Appel de méthodes (8f63bea)
- Opérateurs (6d3c775)
- Définition de méthodes (ed3690f)

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
