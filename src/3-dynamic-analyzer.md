# Analyse dynamique

## Analyse dynamique

- Les annotations ne sont pas de simples commentaires
    - Elles ont un sens sémantique
- On peut les récupérer pour les analyser

## Analyse dynamique

- Ces annotations sont exposées en Python, notamment à l'aide d'`annotationlib`

```python
import annotationlib
annotationlib.get_annotations(addition)
```

## Analyse dynamique

- On peut imaginer les exploiter pour vérifier les types à l'exécution

```python
import inspect

def check_types(func):
    annotations = annotationlib.get_annotations(func)
    sig = inspect.signature(func)

    def wrapper(*args, **kwargs):
        bound_args = sig.bind(*args, **kwargs)
        for name, value in bound_args.arguments.items():
            if not isinstance(value, annotations[name]):
                raise TypeError(f'Invalid type for parameter {name}')

        ret = func(*args, **kwargs)
        if not isinstance(ret, annotations['return']):
            raise TypeError('Invalid return type')

        return ret

    return wrapper
```

## Analyse dynamique

- Et l'essayer avec quelques tests

```python
@check_types
def addition(a: int, b: int) -> int:
    return a + b
```

```python
addition(3, 5)
```

```python
addition('foo', 'bar')
```

## Analyse dynamique

- Mais cela se limite aux branches effectivement parcourues lors de l'exécution
- L'usage dynamique des annotations reste utile dans d'autres domaines
    - sérialisation de données avec `pydantic` par exemple

    ```python
    class MyModel(pydantic.BaseModel):
        name: str
        value: int
    ```
