# Typage statique

## Typage statique

- Annotations apparues en Python 3
    - Standardisées en annotations de types avec Python 3.5
- Forment une couche facultative de typage statique

---

```python
def addition(a: int, b: int) -> int:
    return a + b
```

- La fonction pourrait fonctionner avec des objets `str` mais se limite aux `int`
- Les types abstraits vus précédemment peuvent aussi être utilisés comme annotations

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

## Analyse statique

- L'analyse statique permet d'avaluer toutes les branches du programme
    - analyse le code sans l'exécuter
    - ne connaît donc pas toutes les conditions / données

## mypy

- Analyseur statique de types

```python
%%writefile samples/test_mypy.py
def addition(a: int, b: int) -> int:
    return a + b

x: int = addition(3, 5)
y: float = addition(1, 1)
z: list = addition(0, 0)
addition('foo', 'bar')
```

```shell
mypy samples/test_mypy.py
```

## Typage structurel 🦆

- Le duck-typing n'est pas vraiment compatible avec un typage statique
    - mais trouve un équivalent avec le typage structurel
    - typage structurel : décrire statiquement une interface sans forcer un quelconque type

```python
import numbers

def addition(a: numbers.Number, b: numbers.Number) -> numbers.Number:
    return a + b
```

## Autres fonctionnalités

- Unions de type : `int | float`, `str | None`
- Types composés : `list[int]`, `tuple[str, str]`

---

- Types génériques

    ```python
    class MyType[T]:
        values: list[T]

    obj: MyType[int]
    ```

## Autres fonctionnalités

- Protocoles (typage structurel)

    ```python
    class Iterator[T]:
        def __next__(self) -> T:
            ...

    class Iterable[T]:
        def __iter__(self) -> Iterator[T]:
            ...

    a: Iterable[int] = [1, 2, 3]
    b: Iterable[int] = range(10)
    ```
