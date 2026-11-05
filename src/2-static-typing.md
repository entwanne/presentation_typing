# Typage statique

## Typage statique

- Annotations apparues en Python 3
    - Standardisées en annotations de types avec Python 3.5
- Forment une couche facultative de typage statique
    - Un sous-ensemble (typé) du langage Python
- Peuvent s'apposer aux variables, paramètres, fonctions, etc.

## Annotations de types

```python
def addition(a: int, b: int) -> int:
    return a + b
```

- La fonction pourrait fonctionner avec des objets `str` mais se limite aux `int`
- Les types abstraits vus précédemment peuvent aussi être utilisés comme annotations

## Analyse des annotations

- Vérification du typage à l'aide de mypy

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

## Expressions de types

- On peut formaliser des unions entre types

    ```python
    int | float
    ```

---

- Des types optionnels

    ```python
    str | None
    ```

---

- Mais aussi des types composés

    ```python
    list[int]
    tuple[str, str]
    ```

## Types génériques

- Les types génériques ajoutent une composition dépendant d'un paramètre variable

    ```python
    class MyType[T]:
        values: list[T]

    obj: MyType[int]
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

## Protocoles

- Les protocoles sont un moyen d'écrire une interface pour du typage structurel
    - Il n'est pas nécessaire d'en hériter pour être compatible

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

---

- Il n'existe pas (encore) d'intersection entre protocoles

## Annotations de type

- Attention à ne pas être trop restrictif dans le typage
- Ça continue d'évoluer, chaque version de Python ajoute ses nouveautés
    - Le typage devient plus complet mais aussi plus complexe
