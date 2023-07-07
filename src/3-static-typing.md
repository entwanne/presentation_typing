# My hints will go on

## My hints will go on

- The first goal of type hints is to do static analysis
- Type checkers may use Python AST parser to perform that

---

```pycon
>>> import ast
>>> tree = ast.parse('''
... def addition(a: int, b: int) -> int:
...     return a + b
...
... addition(3, 4)
... addition(3, b=4)
... addition(3, 'x')
... addition(3, b='x')
... ''')
>>> tree
```

---

```pycon
>>> ast.dump(tree)
```

## My hints will go on

- We can extract annotations from this AST

```pycon
>>> tree.body[0].args.args[0].annotation.id
```

---

```pycon
>>> eval(tree.body[0].args.args[0].annotation.id)
```


## My hints will go on

- And so automatize it to get all signatures (naive implementation — no scopes)
- With the help of AST visitor pattern

```python
class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.defs = {}

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        args = node.args.posonlyargs + node.args.args
        kwargs = node.args.args + node.args.kwonlyargs
        args_types = [eval(arg_node.annotation.id) for arg_node in args]
        kwargs_types = {arg_node.arg: eval(arg_node.annotation.id) for arg_node in kwargs}
        return_type = eval(node.returns.id)
        self.defs[node.name] = (args_types, kwargs_types, return_type)
```

---

```pycon
functions = FunctionVisitor()
functions.visit(tree)
print(functions.defs)
```


## My hints will go on

- Then we can check the calls according to these definitions

```python
class CheckVisitor(ast.NodeVisitor):
    def __init__(self, defs):
        self.defs = defs

    def visit_Constant(self, node):
        return type(node.value)

    def visit_Call(self, node):
        name = node.func.id
        func_def = self.defs.get(name)
        if func_def is None:
            print(f'{node.lineno}: Function {name} not found')
        def_args, def_kwargs, _ = func_def

        args = [self.visit(arg) for arg in node.args]
        for i, call_type in enumerate(args):
            if i >= len(def_args):
                print(f'{node.lineno}: Function {name} only takes {len(def_args)} positional arguments')
            elif not issubclass(call_type, def_args[i]):
                print(f'{node.lineno}: Invalid type for argument of function {name}: {def_args[i]} expected, received {call_type}')

        kwargs = {kwarg.arg: self.visit(kwarg.value) for kwarg in node.keywords}
        for arg_name, call_type in kwargs.items():
            if arg_name not in def_kwargs:
                print(f'{node.lineno}: Function {name} does not accept {arg_name!r} keyword argument')
            elif not issubclass(call_type, def_kwargs[arg_name]):
                print(f'{node.lineno}: Invalid type for argument {arg_name} of function {name}: {def_kwargs[arg_name]} expected, received {call_type}')

```

## My hints will go on

```pycon
>>> check = CheckVisitor(functions.defs)
>>> check.visit(tree)
```
