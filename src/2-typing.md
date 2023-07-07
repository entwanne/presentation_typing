# I'm a type!

## I'm a type!

- Python 3.5 introduced annotations
- They allow usage of type hints

---

```python
def addition(a: Number, b: Number) -> Number:
    return a + b
```


## I'm a type!

- They have no effect by default

```pycon
>>> addition(3, 5)
```

---

```pycon
>>> addition('3', '5')
```


## I'm a type!

- But they can be used for documentation purpose
- Indeed, they are exposed in function doc

```pycon
>>> help(addition)
```

---

- And its signature

```pycon
>>> import inspect
>>> inspect.signature(addition)
```


## I'm a type!

- Then we are able to extract them from a function

```pycon
>>> sig = inspect.signature(addition)
>>> sig.parameters['a'].annotation
```

```pycon
>>> sig.return_annotation
```


## I'm a type!

- Or directly with `get_annotations` or `__annotations__` (but less powerful)

```pycon
>>> inspect.get_annotations(addition)
```

```pycon
>>> addition.__annotations__
```

---

- `get_annotations` can resolve lazy annotations

```python
def addition(a: 'Number', b: 'Number') -> 'Number':
    return a + b
```

```pycon
>>> inspect.get_annotations(addition)
```

---

```pycon
>>> inspect.get_annotations(addition, eval_str=True)
```


## I'm a type!

- We can use them to make a runtime type-checker

```python
import functools

def type_checked(func):
    sig = inspect.signature(func)
    ret_type = t if (t := sig.return_annotation) is not inspect._empty else object
    arg_types = {p.name: p.annotation for p in sig.parameters.values() if p.annotation is not inspect._empty}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)

        for name, value in bound.arguments.items():
            arg_type = arg_types.get(name, object)
            if not isinstance(value, arg_type):
                raise TypeError(f"Invalid type for argument {name}: {type(value)}")

        ret = func(*bound.args, **bound.kwargs)
        if not isinstance(ret, ret_type):
            raise TypeError(f"Invalid return type: {type(ret)}")

        return ret

    return wrapper
```


## I'm a type!

```python
@type_checked
def addition(a: Number, b: Number) -> Number:
    return a + b
```

---

```pycon
>>> addition(3, 5)
```

---

```pycon
>>> addition('3', '5')
```


## I'm a type!

- We can also get annotations from a class

---

```python
class Payout:
    id: int
    external_id: str
    amount: int
```

```pycon
>>> inspect.get_annotations(Payout)
```


## I'm a type!

- And use them for other purposes than type checking
- Like pydantic does

---

```python
_loaders = {}

def load(data, cls):
    for parent in cls.mro():
        if loader := _loaders.get(parent):
            return loader(data, cls)
    raise ValueError(f"No loader for type {cls}")

def register_loader(obj_type):
    def decorator(func):
        _loaders[obj_type] = func
        return func
    return decorator
```


## I'm a type!

```python
@register_loader(int)
@register_loader(str)
def _load_scalar(data, cls):
    return cls(data)

@register_loader(object)
def _load_object(data, cls):
    attrs = {}

    for name, value_type in inspect.get_annotations(cls).items():
        attrs[name] = load(data[name], value_type)

    obj = cls.__new__(cls)
    obj.__dict__.update(attrs)
    return obj
```


## I'm a type!

```pycon
>>> payout = load({'id': 12, 'external_id': 'payout_abc', 'amount': 100}, Payout)
>>> vars(payout)
```

---

```pycon
>>> payout = load({'id': 12.3, 'external_id': 5, 'amount': '300'}, Payout)
>>> vars(payout)
```


# I'm a type!

- Types can also be composed

```pycon
>>> list[int]
```

```pycon
>>> dict[str, Payout]
```

---

- These type parameters are exposed in `__args__` attribute

```pycon
>>> list[int].__args__
```


# I'm a type!

- Let's use that for our object-loader!

```python
@register_loader(list)
def _load_list(data, cls):
    item_cls, = cls.__args__
    return [load(item, item_cls) for item in data]
```

---

```python
class PayoutEvent:
    type: str

class Payout:
    id: int
    external_id: str
    amount: int
    events: list[PayoutEvent]
```


# I'm a type!

```pycon
>>> payout = load({'id': 12, 'external_id': 'payout_abc', 'amount': 100, 'events': [{'type': 'pending'}, {'type': 'rejected'}]}, Payout)
>>> vars(payout)
```

---

```pycon
>>> vars(payout.events[0])
```
